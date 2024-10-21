from PIL import Image

# Create a blank canvas (width, height) with a white background
width, height = 200, 200
canvas = Image.new('RGB', (width, height), 'white')

# Get the pixel map of the canvas
pixels = canvas.load()

# Define the pixels that form the object
object_pixels = [
    (50, 50), (51, 50), (52, 50), (50, 51), (51, 51), (52, 51), # A small square
    (100, 100), (101, 100), (102, 100), (100, 101), (101, 101), (102, 101) # Another small square
]

# Set the object pixels to a specific color (e.g., red)
for pixel in object_pixels:
    pixels[pixel] = (255, 0, 0)  # RGB for red

# Show or save the image
canvas.show()  # To display the canvas
canvas.save('canvas.png')  # To save the canvas as an image
