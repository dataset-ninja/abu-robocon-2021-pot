import supervisely as sly
import os
from dataset_tools.convert import unpack_if_archive
import src.settings as s
from urllib.parse import unquote, urlparse
from supervisely.io.fs import get_file_name, get_file_ext, file_exists
import shutil

from tqdm import tqdm

def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:        
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path
    
def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count
    
def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    ### Function should read local dataset and upload it to Supervisely project, then return project info.###
    label_data_path = os.path.join("robo","img","img")
    no_label_data_path = os.path.join("robo","NegativeImages_raw")
    batch_size = 30
    images_ext = ".jpg"
    masks_ext = ".txt"
    

    def create_ann(image_path):
        labels = []

        camera_value_index = get_file_name(image_path).split("_")[0]
        camera_value = index_to_camera.get(camera_value_index)
        if camera_value is None:
            camera_value = "arbitrary_device"
        camera = sly.Tag(tag_camera, value=camera_value)

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        mask_path = os.path.join(label_data_path, get_file_name(image_path) + masks_ext)

        if file_exists(mask_path):
            with open(mask_path) as f:
                content = f.read().split("\n")

                for curr_data in content:
                    if len(curr_data) != 0:
                        curr_data = list(map(float, curr_data.split(" ")))

                        left = int((curr_data[1] - curr_data[3] / 2) * img_wight)
                        right = int((curr_data[1] + curr_data[3] / 2) * img_wight)
                        top = int((curr_data[2] - curr_data[4] / 2) * img_height)
                        bottom = int((curr_data[2] + curr_data[4] / 2) * img_height)
                        rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
                        label = sly.Label(rectangle, obj_class)
                        labels.append(label)
        if not labels:
            print(get_file_name(image_path))

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=[camera])


    obj_class = sly.ObjClass("pot", sly.Rectangle)

    tag_camera = sly.TagMeta(
        "camera",
        sly.TagValueType.ONEOF_STRING,
        possible_values=["realsence_d455", "azure_kinect", "realsence_l515_lidar", "arbitrary_device"],
    )
    tag_subfolder = sly.TagMeta("subfolder", sly.TagValueType.ANY_STRING)

    index_to_camera = {
        "D455": "realsence_d455",
        "K4A": "azure_kinect",
        "L515": "realsence_l515_lidar",
    }

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(
        obj_classes=[obj_class],
        tag_metas=[tag_camera, tag_subfolder],
    )
    api.project.update_meta(project.id, meta.to_json())

    images_names = [
        im_name for im_name in os.listdir(label_data_path) if get_file_ext(im_name) == images_ext
    ]

    ds_name = "labelled"

    dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

    progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

    for img_names_batch in sly.batched(images_names, batch_size=batch_size):
        images_pathes_batch = [
            os.path.join(label_data_path, image_path) for image_path in img_names_batch
        ]

        img_infos = api.image.upload_paths(dataset.id, img_names_batch, images_pathes_batch)
        img_ids = [im_info.id for im_info in img_infos]

        anns_batch = [create_ann(image_path) for image_path in images_pathes_batch]
        api.annotation.upload_anns(img_ids, anns_batch)

        progress.iters_done_report(len(img_names_batch))


    def create_ann_neg(image_path):
        labels = []

        sub = sly.Tag(tag_subfolder, value=subfolder)

        camera_value_index = get_file_name(image_path).split("_")[0]
        camera_value = index_to_camera.get(camera_value_index)
        if camera_value is None:
            camera_value = "arbitrary_device"
        camera = sly.Tag(tag_camera, value=camera_value)

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        return sly.Annotation(
            img_size=(img_height, img_wight), labels=labels, img_tags=[camera, sub]
        )


    ds_name = "negativeimages_raw"

    dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

    progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

    for subfolder in os.listdir(no_label_data_path):
        images_path = os.path.join(no_label_data_path, subfolder)
        images_names = os.listdir(images_path)

        progress = sly.Progress(
            "Create dataset {}, add {} data".format(ds_name, subfolder), len(images_names)
        )

        for img_names_batch in sly.batched(images_names, batch_size=batch_size):
            images_pathes_batch = [
                os.path.join(images_path, image_path) for image_path in img_names_batch
            ]

            img_names_batch = [subfolder + "_" + im_name for im_name in img_names_batch]

            img_infos = api.image.upload_paths(dataset.id, img_names_batch, images_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns_batch = [create_ann_neg(image_path) for image_path in images_pathes_batch]
            api.annotation.upload_anns(img_ids, anns_batch)

            progress.iters_done_report(len(img_names_batch))
    
    return project
