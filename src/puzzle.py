import os

import matplotlib.pyplot as plt
import numpy as np
from skimage import io, transform

img_model = io.imread(os.path.join('resources', 'city', 'model.jpg'))
img_puzzle = io.imread(os.path.join('resources', 'city', 'puzzle.jpg'))

PUZZLE_WIDTH = 118.4
PUZZLE_HEIGHT = 84.5


def warp_image(img, coords, output_shape):
    src = np.array([[0, 0], [0, img_model.shape[0]], [img_model.shape[1], img_model.shape[0]], [img_model.shape[1], 0]])
    dst = np.array(coords)

    project_transform = transform.ProjectiveTransform()
    project_transform.estimate(src=np.array(src), dst=np.array(dst))

    warped = transform.warp(img, project_transform, output_shape=output_shape)
    return warped


def create_mask(img):
    return np.argwhere((img[:, :, 0] > 0.99)
                       & (img[:, :, 1] == 0.0)
                       & (img[:, :, 2] == 0.0))


img_model_warp = warp_image(img_model, [[222, 219], [129, 2823], [3906, 2745], [3804, 261]], img_puzzle.shape)
img_puzzle_warp = warp_image(img_puzzle, [[357, 198], [0, 2685], [3981, 2766], [3711, 195]], img_puzzle.shape)

plt.imshow(img_model_warp)
plt.show()

plt.imshow(img_puzzle_warp)
plt.show()

mask_indices = create_mask(img_puzzle_warp)
mask_x_min, mask_x_max = mask_indices[:, 0].min(), mask_indices[:, 0].max()
mask_y_min, mask_y_max = mask_indices[:, 1].min(), mask_indices[:, 1].max()

piece = img_model_warp.copy()
piece = piece[mask_x_min:mask_x_max + 1, mask_y_min:mask_y_max + 1, :]

mask_indices_piece = mask_indices - np.array([mask_x_min, mask_y_min])
# mask_indices_piece = np.expand_dims(mask_indices_piece, axis=2)

boolean_mask = np.ones_like(piece)
for (i, j) in mask_indices_piece:
    boolean_mask[i, j, :] = piece[i, j, :]

plt.imshow(boolean_mask)
plt.show()

plt.imshow(piece)
plt.show()

width = PUZZLE_WIDTH * piece.shape[0] / img_model_warp.shape[0]
height = PUZZLE_HEIGHT * piece.shape[1] / img_model_warp.shape[1]
# plt.imsave(os.path.join('resources', 'city', f'piece_{width}x{height}cm.jpg'), piece)
