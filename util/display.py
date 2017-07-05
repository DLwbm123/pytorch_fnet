from aicsimage.io import omeTifWriter
import numpy as np
import matplotlib.pyplot as plt
from util import find_z_of_max_slice
from util import print_array_stats
import pdb

def plot_logger_data():
    x, y = logger.log['num_iter'], logger.log['loss']
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_axes((1, 1, 1, .3), label='training loss')
    ax.plot(x, y)
    ax.set_xlabel('training iteration')
    ax.set_ylabel('MSE loss')
    plt.show()

def show_img(ar):
    import PIL
    import PIL.ImageOps
    from IPython.core.display import display
    img_norm = ar - ar.min()
    img_norm *= 255./img_norm.max()
    img_pil = PIL.Image.fromarray(img_norm).convert('L')
    display(img_pil)
    
def draw_rect(img, coord_tl, dims_rect, thickness=3, color=0):
    """Draw rectangle on image.

    Parameters:
    img - 2d numpy array (image is modified)
    coord_tl - coordinate within img to be top-left corner or rectangle
    dims_rect - 2-value tuple indicated the dimensions of the rectangle

    Returns:
    None
    """
    assert len(img.shape) == len(coord_tl) == len(dims_rect) == 2
    for i in range(thickness):
        if (i+1)*2 <= dims_rect[0]:
            # create horizontal lines
            img[coord_tl[0] + i, coord_tl[1]:coord_tl[1] + dims_rect[1]] = color
            img[coord_tl[0] + dims_rect[0] - 1 - i, coord_tl[1]:coord_tl[1] + dims_rect[1]] = color
        if (i+1)*2 <= dims_rect[1]:
            # create vertical lines
            img[coord_tl[0]:coord_tl[0] + dims_rect[0], coord_tl[1] + i] = color
            img[coord_tl[0]:coord_tl[0] + dims_rect[0], coord_tl[1] + dims_rect[1] - 1 - i] = color

def display_batch(vol_light_np, vol_nuc_np, batch):
    """Display images of examples from batch.
    vol_light_np - numpy array
    vol_nuc_np - numpy array
    batch - 3-element tuple: chunks from vol_light_np, chunks from vol_nuc_np, coordinates of chunks
    """
    n_chunks = batch[0].shape[0]
    z_max_big = find_z_of_max_slice(vol_nuc_np)
    img_light, img_nuc = vol_light_np[z_max_big], vol_nuc_np[z_max_big]
    chunk_coord_list = batch[2]
    dims_rect = batch[0].shape[-2:]  # get size of chunk in along yz plane
    min_light, max_light = np.amin(vol_light_np), np.amax(vol_light_np)
    min_nuc, max_nuc = np.amin(vol_nuc_np), np.amax(vol_nuc_np)
    for i in range(len(chunk_coord_list)):
        coord = chunk_coord_list[i][1:]  # get yx coordinates
        draw_rect(img_light, coord, dims_rect, thickness=2, color=min_light)
        draw_rect(img_nuc, coord, dims_rect, thickness=2, color=min_nuc)

    # display originals
    # fig = plt.figure(figsize=(12, 6))
    # fig.suptitle('slice at z: ' + str(z_max_big))
    # ax = fig.add_subplot(121)
    # ax.get_xaxis().set_visible(False)
    # ax.get_yaxis().set_visible(False)
    # ax.imshow(img_light, cmap='gray', interpolation='bilinear', vmin=-3, vmax=3)
    # ax = fig.add_subplot(122)
    # ax.get_xaxis().set_visible(False)
    # ax.get_yaxis().set_visible(False)
    # ax.imshow(img_nuc, cmap='gray', interpolation='bilinear', vmin=-3, vmax=3)
    # plt.show()

    print('light volume slice | z =', z_max_big)
    show_img(img_light)
    print('-----')
    print('nuc volume slice | z =', z_max_big)
    show_img(img_nuc)

    # display chunks
    z_mid_chunk = batch[0].shape[2]//2  # z-dim
    for i in range(n_chunks):
        title_str = 'chunk: ' + str(i) + ' | z:' + str(z_mid_chunk)
        fig = plt.figure(figsize=(9, 4))
        fig.suptitle(title_str)
        img_chunk_sig = batch[0][i, 0, z_mid_chunk, ]
        img_chunk_tar = batch[1][i, 0, z_mid_chunk, ]
        ax = fig.add_subplot(1, 2, 1)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.imshow(img_chunk_sig, cmap='gray', interpolation='bilinear')
        ax = fig.add_subplot(1, 2, 2)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.imshow(img_chunk_tar, cmap='gray', interpolation='bilinear')
        plt.show()

def save_img_np(img_np, fname):
    """Save image (numpy array, ZYX) as a TIFF."""
    with omeTifWriter.OmeTifWriter(fname, overwrite_file=True) as fo:
        fo.save(img_np)
        print('saved:', fname)
            

def display_visual_eval_images(signal, target, prediction):
    """Display 3 images: light, nuclear, predicted nuclear.

    Parameters:
    signal (5d numpy array)
    target (5d numpy array)
    prediction (5d numpy array)
    """
    n_examples = signal.shape[0]
    # print('Displaying chunk slices for', n_examples, 'examples')
    source_list = [signal, target, prediction]
    titles = ('transmitted', 'DNA', 'predicted')
            
    for ex in range(n_examples):
        # fig = plt.figure(figsize=(15, 15), tight_layout={'w_pad':1.0})
        fig = plt.figure(figsize=(15, 15))
        fig.subplots_adjust(wspace=0.05)
        z_strong = find_z_of_max_slice(target[ex, 0, ])
        print('z:', z_strong)
        print('DNA channel stats:')
        print_array_stats(target)
        for i in range(3):
            img = source_list[i][ex, 0, z_strong, ]
            ax = fig.add_subplot(1, 3, i + 1)
            ax.set_title(titles[i])
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            # ax.imshow(img, cmap='gray', interpolation='bilinear', vmin=0, vmax=1)
            ax.imshow(img, cmap='gray', interpolation='bilinear')
    plt.show()

if __name__ == '__main__':
    print('util.display')