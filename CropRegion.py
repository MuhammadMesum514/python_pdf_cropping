
# # Importing Image class from PIL module
# from PIL import Image

# # Opens a image in RGB mode
# im = Image.open(r"testImg.jpg")

# # Size of the image in pixels (size of original image)
# # (This is not mandatory)
# width, height = im.size

# # read images from output_images folder loop over them and crop. save them into a new directory named output_cropped_images



# # Setting the points for cropped image
# left = 95
# top = 95
# right = 1230
# bottom = 1270

# # Cropped image of above dimension
# # (It will not change original image)
# im1 = im.crop((left, top, right, bottom))

# # Shows the image in image viewer
# im1.show()
# im1.save("cropped.jpg")


import os
from PIL import Image

input_dir = 'output_images'
output_dir = 'output_cropped_images'


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# get file count in the directory
file_count = len([name for name in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, name))])
print(f"Total files in the directory: {file_count}")

# Loop over the images in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        
        img_path = os.path.join(input_dir, filename)
        im = Image.open(img_path)
        
        left = 95
        top = 130   
        right = 1630
        bottom = 0
        if filename == f"page_{file_count}.png":
            bottom = 1750
        else:
            bottom = 2160
        print(f" page_{file_count}.png")
        print(f"Processing {filename} with dimensions: {left}, {top}, {right}, {bottom}")
        im1 = im.crop((left, top, right, bottom))
        
        # Save the cropped image to the output directory
        cropped_img_path = os.path.join(output_dir, filename)
        im1.save(cropped_img_path)