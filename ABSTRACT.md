Author introduce the **ABU Robocon 2021 Pot** dataset, this collection of labeled RGB images, expertly organized in the YOLOv4 style, provides a unique and valuable resource for researchers and enthusiasts in the field of robotics and computer vision. This dataset comprises 1552 images in *labelled* split, with 1304 images meticulously marked to precisely identify the *pot* class, and an additional 322 images in the *negativeimages_raw* split, which may have been utilized for further experimentation and training. This comprehensive dataset is poised to empower future Robocon contestants and researchers, equipping them with the tools needed to tackle the distinctive challenges presented by the ABU Robocon Pot in the context of object detection and robotic competition.

file prefix explanation in img folder:

D455_ : the RGB image is obtained from ***realsence_d455*** depth camera.
K4A_: the RGB image is obtained from ***azure_kinect*** depth camera.
L515_: the RGB image is obtained from ***realsence_l515_lidar***.

Rb2017, Rb2018, Rb2019, Rb2020, Rb2021: the RGB image obtained by ***arbitrary_device*** with blank label. Basically used to reduce false positive of detection.

You could instead use the images in the folder NegativeImages_raw as negative samples for any purpose to boost your model detection for Robocon. This folder contain random photos from previous ABU Robocon in Hong Kong Science Park.
