import numpy as np
import cv2

# Load the background image
background_image = cv2.imread('static/download2.jpg')  # Replace 'background.jpg' with the path to your background image
background_image = cv2.resize(background_image, (400, 400))

# Create a blank canvas with an alpha channel
canvas = np.zeros((background_image.shape[0], background_image.shape[1], 4), dtype=np.uint8)
canvas[:, :, :3] = background_image

# Define the colors
outer_circle_color = (255, 0, 0, 255)    # Blue (with full opacity)
half_filled_color = (0, 255, 255, 255)  # Yellow (with full opacity)
transparent_color = (0, 0, 0, 0)         # Fully transparent color

# Calculate the center and radius of the circles
canvas_size = (canvas.shape[1], canvas.shape[0])  # Use the size of the background image
center = (canvas_size[0] // 2, canvas_size[1] // 2)
outer_radius = min(canvas_size[0], canvas_size[1]) // 2 - 20
inner_radius = outer_radius // 2

# Draw the outer circle
cv2.circle(canvas, center, outer_radius, outer_circle_color, thickness=-1)

# Draw the half-filled portion
start_angle = 90  # Adjust the angle as needed
end_angle = 270  # Adjust the angle as needed
cv2.ellipse(canvas, center, (outer_radius, outer_radius), 0, start_angle, end_angle, half_filled_color, thickness=-1)

# Save the result as a PNG image with transparency
cv2.imwrite("donut_with_transparent_inner_circle.png", canvas)

# Display the result
cv2.imshow("Donut", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()
