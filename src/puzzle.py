import argparse
import os

import numpy as np
from PIL import Image
from skimage import transform


def warp_image(img, coords, output_shape):
    src = np.array([[0, 0], [0, img.shape[0]], [img.shape[1], img.shape[0]], [img.shape[1], 0]])
    dst = np.array(coords)

    project_transform = transform.ProjectiveTransform()
    project_transform.estimate(src=np.array(src), dst=np.array(dst))

    warped = transform.warp(img, project_transform, output_shape=output_shape)
    return warped


def generate_piece(img_model, img_puzzle, img_mask) -> Image.Image:
    mask_indices = np.argwhere(img_mask == 1.0)
    mask_x_min, mask_x_max = mask_indices[:, 0].min(), mask_indices[:, 0].max()
    mask_y_min, mask_y_max = mask_indices[:, 1].min(), mask_indices[:, 1].max()

    piece = img_model[mask_x_min:mask_x_max + 1, mask_y_min:mask_y_max + 1, :]
    alpha_channel = img_mask[mask_x_min:mask_x_max + 1, mask_y_min:mask_y_max + 1]

    piece = np.dstack((piece, alpha_channel))
    piece = Image.fromarray((255 * piece).astype(np.uint8))

    return piece


def main(args):
    model_photo = np.array(Image.open(args.model_photo_path))
    puzzle_photo = np.array(Image.open(args.puzzle_photo_path))

    mask_img = np.array(Image.open(args.mask_img_path))

    # output_shape = (10 * args.puzzle_width, 10 * args.puzzle_height)
    output_shape = puzzle_photo.shape

    model_photo_vertices = [222, 219], [129, 2823], [3906, 2745], [3804, 261]
    model_photo_warped = warp_image(model_photo, coords=model_photo_vertices, output_shape=output_shape)

    puzzle_photo_vertices = [[357, 198], [0, 2685], [3981, 2766], [3711, 195]]
    puzzle_photo_warped = warp_image(puzzle_photo, coords=puzzle_photo_vertices, output_shape=output_shape)
    mask_img_warped = warp_image(mask_img, coords=puzzle_photo_vertices, output_shape=output_shape)

    piece = generate_piece(model_photo_warped, puzzle_photo_warped, mask_img_warped)

    if args.output_path is None:
        output_path = args.puzzle_photo_path.split(os.path.sep)[:-1]
        output_path = os.path.sep.join(output_path)
    else:
        output_path = args.output_path

    piece.save(os.path.join(output_path, 'piece.png'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser('')
    parser.add_argument('model_photo_path', type=str, help='Path to the photo of the puzzle model (i.e. box reference)')
    parser.add_argument('puzzle_photo_path', type=str, help='Path to the photo of the incomplete puzzle')
    # TODO: Remove and obtain from puzzle_photo_path
    parser.add_argument('mask_img_path', type=str)
    parser.add_argument('puzzle_width', type=float, help='Puzzle width in CM')
    parser.add_argument('puzzle_height', type=float, help='Puzzle height in CM')
    parser.add_argument('--output_path', help='Path to store the resulting missing piece image. If ignored, it will be'
                                              'saved to the same folder as the source images', default=None)

    main(parser.parse_args())
