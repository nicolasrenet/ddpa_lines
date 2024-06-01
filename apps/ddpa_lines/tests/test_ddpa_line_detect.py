#!/usr/env python3

import unittest
from torch import Tensor
from pathlib import Path
#from apps.ddpa_lines import seglib
import logging
import pytest
from PIL import Image
from torch import Tensor
import json
import numpy as np
import torch
import skimage as ski
from matplotlib import pyplot as plt

import sys

# Append app's root directory to the Python search path
sys.path.append( str( Path(__file__).parents[1] ) )

import seglib



@pytest.fixture(scope="module")
def data_path():
    return Path( __file__ ).parent.joinpath('data')

def test_dummy( data_path):
    """
    A dummy test, as a sanity check for the test framework.
    """
    print(data_path)
    assert seglib.dummy() == True

def test_line_segmentation_model_not_found(  data_path ):
    """
    An exception should be raised when no segmentation model found.
    """
    model = Path('nowhere_to_be_found.mlmodel')
    input_image = data_path.joinpath('NA-ACK_14201223_01485_r-r1.png')
    with pytest.raises( FileNotFoundError ) as e:
        seglib.line_segment(input_image, model)

def test_binary_mask_from_image_real_img( data_path):
    """
    Binarization function should return a Boolean tensor with shape( h,w )
    """
    input_img = Image.open( data_path.joinpath('NA-ACK_14201223_01485_r-r1_reduced.png'))
    mask = seglib.get_mask( input_img )
    assert type(mask) == torch.Tensor 
    assert mask.dtype == torch.bool
    assert mask.shape == tuple(reversed(input_img.size))

def test_binary_mask_from_image_fg_bg():
    """
    Binary map should be 1 for FG pixels, 0 otherwise.
    """
    img_arr = np.full((15,15,3), 200, dtype=np.uint8 ) # background
    img_arr[8,8]=5 # foreground = 1 pixel
    binary_map = seglib.get_mask( Image.fromarray( img_arr) )
    assert binary_map[8,8] == 1 # single FG pixel = T
    assert torch.sum(binary_map).item() == 1 # remaining pixels = F

def test_array_to_rgba_uint8():
    """
    Conversion of a 1-channel 32-bit unsigned int array yields a 4-channel tensor.
    """
    arr = np.array( [[2,2,2,0,0,0],
                     [2,2,2,0,0,0],
                     [2,2,0x203,3,0,0],
                     [0,0,3,3,3,0],
                     [0,0,0,0,0,0],
                     [0,0x40102,0,0,0,0]], dtype='int32')
    tensor = seglib.array_to_rgba_uint8( arr )
    assert torch.equal( tensor,
        torch.tensor([[[2, 2, 2, 0, 0, 0],
                       [2, 2, 2, 0, 0, 0],
                       [2, 2, 3, 3, 0, 0],
                       [0, 0, 3, 3, 3, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 2, 0, 0, 0, 0]],
                      [[0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 2, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 1, 0, 0, 0, 0]],
                      [[0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 4, 0, 0, 0, 0]],
                      [[0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0]]], dtype=torch.uint8))


def test_rgba_uint8_to_hw_tensor():
    """
    Conversion of a 1-channel 32-bit unsigned int array yields a 4-channel tensor.
    """
    tensor = torch.tensor([[[2, 2, 2, 0, 0, 0],
                            [2, 2, 2, 0, 0, 0],
                            [2, 2, 3, 3, 0, 0],
                            [0, 0, 3, 3, 3, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 2, 0, 0, 0, 0]],

                           [[0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 2, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0]],

                           [[0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 4, 0, 0, 0, 0]],

                           [[0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0]]], dtype=torch.uint8)

    assert np.array_equal( seglib.rgba_uint8_to_hw_tensor( tensor ),
                    torch.tensor( [[2,2,2,0,0,0],
                                   [2,2,2,0,0,0],
                                   [2,2,0x203,3,0,0],
                                   [0,0,3,3,3,0],
                                   [0,0,0,0,0,0],
                                   [0,0x40102,0,0,0,0]], dtype=torch.int32))


def test_flat_to_cube_and_other_way_around():
    """
    A flat map that is stored into a cube and then retrieved back as a map should contain
    the same values as the original.
    """
    a = np.random.randint(120398, size=(7,5), dtype=np.int32 )
    assert torch.equal( torch.from_numpy( a ), seglib.rgba_uint8_to_hw_tensor( seglib.array_to_rgba_uint8(a) ))

def test_polygon_mask_to_polygon_map_32b_store_single_polygon():
    """
    Storing polygon (as binary mask + label) on empty tensor yields correct map
    """
    label_map = np.zeros((6,6), dtype='int32')
    polygon_mask = np.array( [[1,1,1,0,0,0],
                              [1,1,1,0,0,0],
                              [1,1,1,0,0,0],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0]], dtype='int32')
    seglib.apply_polygon_mask_to_map(label_map, polygon_mask, 2)

    assert np.array_equal( label_map,
                   np.array( [[2,2,2,0,0,0],
                              [2,2,2,0,0,0],
                              [2,2,2,0,0,0],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0]], dtype='int32'))

def test_polygon_mask_to_polygon_map_32b_store_two_intersecting_polygons():
    """
    Storing extra polygon (as binary mask + labels) on labeled tensor yields correct map
    """
    label_map = np.array( [[2,2,2,0,0,0],
                           [2,2,2,0,0,0],
                           [2,2,2,0,0,0],
                           [0,0,0,0,0,0],
                           [0,0,0,0,0,0],
                           [0,0,0,0,0,0]], dtype='int32')

    polygon_mask = np.array( [[0,0,0,0,0,0],
                              [0,0,0,0,0,0],
                              [0,0,1,1,0,0],
                              [0,0,1,1,1,0],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0]], dtype='int32')

    seglib.apply_polygon_mask_to_map(label_map, polygon_mask, 3)

    # intersecting pixel has value (l1<<8) + l2
    assert np.array_equal( label_map,
                   np.array( [[2,2,2,0,0,0],
                              [2,2,2,0,0,0],
                              [2,2,0x203,3,0,0],
                              [0,0,3,3,3,0],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0]], dtype='int32'))


def test_polygon_mask_to_polygon_map_32b_store_two_polygons_no_intersection():
    """
    Storing extra polygon (as binary mask + labels) on labeled tensor yields
    2-label map.
    """
    label_map = np.array( [[2,2,2,0,0,0],
                           [2,2,2,0,0,0],
                           [2,2,2,0,0,0],
                           [0,0,0,0,0,0],
                           [0,0,0,0,0,0],
                           [0,0,0,0,0,0]], dtype='int32')

    polygon_mask = np.array( [[0,0,0,0,0,0],
                              [0,0,0,0,0,0],
                              [0,0,0,1,1,0],
                              [0,0,1,1,1,1],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0]], dtype='int32')

    seglib.apply_polygon_mask_to_map(label_map, polygon_mask, 3)

    assert np.array_equal( label_map,
                   np.array( [[2,2,2,0,0,0],
                              [2,2,2,0,0,0],
                              [2,2,2,3,3,0],
                              [0,0,3,3,3,3],
                              [0,0,0,0,0,0],
                              [0,0,0,0,0,0]], dtype='int32'))

def test_polygon_mask_to_polygon_map_32b_store_three_intersecting_polygons():
    """
    Storing 2 extra polygons (as binary mask + labels) on labeled tensor with overlap yields
    map with intersection labels l = l1, l' = (l1<<8) + l2, l''=(l1<<16)+(l2<<8)+l3, ...
    """
    label_map = np.array( [[2,2,2,0,0,0],
                           [2,2,2,0,0,0],
                           [2,2,2,0,0,0],
                           [0,0,0,0,0,0],
                           [0,0,0,0,0,0],
                           [0,0,0,0,0,0]], dtype='int32')

    polygon_mask_1 = np.array( [[0,0,0,0,0,0],
                                [0,0,0,0,0,0],
                                [0,0,1,1,0,0],
                                [0,0,1,1,1,0],
                                [0,0,0,0,0,0],
                                [0,0,0,0,0,0]], dtype='int32')
    seglib.apply_polygon_mask_to_map(label_map, polygon_mask_1, 3)

    polygon_mask_2 = np.array( [[0,0,0,0,0,0],
                                [0,0,0,0,0,0],
                                [0,0,1,1,1,0],
                                [0,0,1,1,1,1],
                                [0,0,1,1,1,0],
                                [0,0,1,1,0,0]], dtype='int32')
    seglib.apply_polygon_mask_to_map(label_map, polygon_mask_2, 4)

    assert np.array_equal( label_map,
                   np.array( [[2,2,2,0,0,0],
                              [2,2,2,0,0,0],
                              [2,2,0x20304,0x304,4,0],
                              [0,0,0x304,0x304,0x304,4],
                              [0,0,4,4,4,0],
                              [0,0,4,4,0,0]], dtype='int32'))


def test_polygon_mask_to_polygon_map_32b_store_large_values():
    """
    Storing 3 polygons with large labels (ex. 255) yields correct map (no overflow)
    """
    label_map = np.array( [[255,255,255,0,0,0],
                           [255,255,255,0,0,0],
                           [255,255,255,0,0,0],
                           [0,0,0,0,0,0],
                           [0,0,0,0,0,0],
                           [0,0,0,0,0,0]], dtype='int32')

    polygon_mask_1 = np.array( [[0,0,0,0,0,0],
                                [0,0,0,0,0,0],
                                [0,0,1,1,0,0],
                                [0,0,1,1,1,0],
                                [0,0,0,0,0,0],
                                [0,0,0,0,0,0]], dtype='int32')
    seglib.apply_polygon_mask_to_map(label_map, polygon_mask_1, 255)

    polygon_mask_2 = np.array( [[0,0,0,0,0,0],
                                [0,0,0,0,0,0],
                                [0,0,1,1,1,0],
                                [0,0,1,1,1,1],
                                [0,0,1,1,1,0],
                                [0,0,1,1,0,0]], dtype='int32')
    seglib.apply_polygon_mask_to_map(label_map, polygon_mask_2, 255)

    assert np.array_equal( label_map,
                   np.array( [[0xff,0xff,0xff,0,0,0],
                              [0xff,0xff,0xff,0,0,0],
                              [0xff,0xff,0xffffff,0xffff,0xff,0],
                              [0,0,0xffff,0xffff,0xffff,0xff],
                              [0,0,0xff,0xff,0xff,0],
                              [0,0,0xff,0xff,0,0]], dtype='int32'))

def test_polygon_mask_to_polygon_map_32b_4_polygon_exception():
    """
    Exception raised when trying to store more than 3 polygons on same pixel.
    """
    label_map = np.array( [[2,2,2,0],
                           [2,2,2,0],
                           [2,2,2,0],
                           [0,0,0,0]], dtype='int32')

    polygon_mask = np.array( [[0,0,0,0],
                              [0,0,0,0],
                              [0,0,1,1],
                              [0,0,0,0]], dtype='int32')

    seglib.apply_polygon_mask_to_map(label_map, polygon_mask, 3)
    seglib.apply_polygon_mask_to_map(label_map, polygon_mask, 3)

    with pytest.raises( ValueError ) as e:
        seglib.apply_polygon_mask_to_map(label_map, polygon_mask, 1)


def test_retrieve_polygon_mask_from_map_no_binary_mask_1():
    label_map = torch.tensor([[[2, 2, 2, 0, 0, 0],
                               [2, 2, 2, 0, 0, 0],
                               [2, 2, 4, 4, 4, 0],
                               [0, 0, 4, 4, 4, 4],
                               [0, 0, 4, 4, 4, 0],
                               [0, 0, 4, 4, 0, 0]],
                              [[0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 3, 3, 0, 0],
                               [0, 0, 3, 3, 3, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0]],
                              [[0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 2, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0]],
                              [[0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0]]], dtype=torch.uint8)

    expected = torch.tensor( [[False, False, False, False, False, False],
                               [False, False, False, False, False, False],
                               [False, False,  True,  True, False, False],
                               [False, False,  True,  True,  True, False],
                               [False, False, False, False, False, False],
                               [False, False, False, False, False, False]])

    assert torch.equal( seglib.retrieve_polygon_mask_from_map(label_map, 3), expected)
    # second call ensures that the map is not modified by the retrieval operation
    assert torch.equal( seglib.retrieve_polygon_mask_from_map(label_map, 3), expected)

def test_retrieve_polygon_mask_from_map_no_binary_mask_2():
    label_map = torch.tensor([[[2, 2, 2, 0, 0, 0],
                               [2, 2, 2, 0, 0, 0],
                               [2, 2, 4, 4, 4, 0],
                               [0, 3, 4, 4, 4, 4],
                               [0, 0, 3, 4, 4, 0],
                               [0, 0, 4, 4, 0, 0]],
                              [[0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 3, 3, 0, 0],
                               [0, 0, 3, 3, 3, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0]],
                              [[0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 2, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0]],
                              [[0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0]]], dtype=torch.uint8)

    assert torch.equal( seglib.retrieve_polygon_mask_from_map(label_map, 3),
                torch.tensor( [[False, False, False, False, False, False],
                               [False, False, False, False, False, False],
                               [False, False,  True,  True, False, False],
                               [False,  True,  True,  True,  True, False],
                               [False, False,  True, False, False, False],
                               [False, False, False, False, False, False]]))


def test_segmentation_dict_to_polygon_map_label_count(  data_path ):
    """
    seglib.dict_to_polygon_map(dict, image) should return a tuple (labels, polygons)
    """
    with open( data_path.joinpath('segdict_NA-ACK_14201223_01485_r-r1+model_20_reduced.json'), 'r') as segdict_file, Image.open( data_path.joinpath('NA-ACK_14201223_01485_r-r1_reduced.png'), 'r') as input_image:
        segdict = json.load( segdict_file )
        polygons = seglib.dict_to_polygon_map( segdict, input_image )
        assert type(polygons) is torch.Tensor
        assert torch.max(polygons) == 4


def test_segmentation_dict_to_polygon_map_polygon_img_type(  data_path ):
    with open( data_path.joinpath('segdict_NA-ACK_14201223_01485_r-r1+model_20_reduced.json'), 'r') as segdict_file, Image.open( data_path.joinpath('NA-ACK_14201223_01485_r-r1_reduced.png'), 'r') as input_image:
        segdict = json.load( segdict_file )
        polygons = seglib.dict_to_polygon_map( segdict, input_image )
        assert polygons.shape == (4,)+input_image.size[::-1]

def test_union_intersection_count_two_maps():
    """
    Provided two label maps that each encode (potentially overlapping) polygons, yield 
    intersection and union counts for each possible pair of labels (i,j) with i ∈  map1
    and j ∈ map2.
    Shared pixels in each map (i.e. overlapping polygons) are counted independently for each polygon.
    """
    # Pred. labels: 2,3,4
    map1 = seglib.array_to_rgba_uint8(np.array([[2,2,2,0,0,0],
                      [2,2,2,0,0,0],
                      [2,2,0x20304,0x304,4,0],
                      [0,0,0x304,0x304,0x304,4],
                      [0,0,4,4,4,0],
                      [0,0,4,0x402,0,0]], dtype='int32'))

    # GT labels: 2,3,4
    map2 = seglib.array_to_rgba_uint8(np.array( [[0,2,2,0,0,0],
                      [2,2,4,2,2,0],
                      [2,2,0x20304,0x304,4,0],
                      [0,3,0x304,0x304,0x304,4],
                      [0,0,3,4,4,0],
                      [0,0,0x204,4,0,0]], dtype='int32'))

    pixel_count = seglib.polygon_pixel_metrics_two_maps( map1, map2 )[:,:,:2]

    c2l, c2r = 8+1/3+.5, 8+1/3+.5
    c3l, c3r = 1/3+.5*4, 1/3+2+.5*4
    c4l, c4r = 1/3+5*.5+6, 1/3+5*.5+6
    i22, i23, i24 = 6+1/3, 1/3, 1+1/3+.5
    i32, i33, i34 = 1/3, 1/3+.5*4, 1/3+.5*4
    i42, i43, i44 = 1/3+.5, 1/3+.5*4+1, 1/3+.5*6+4
    u22, u23, u24 = c2l+c2r-i22, c2l+c3r-i23, c2l+c4r-i24
    u32, u33, u34 = c3l+c2r-i32, c3l+c3r-i33, c3l+c4r-i34
    u42, u43, u44 = c4l+c2r-i42, c4l+c3r-i43, c4l+c4r-i44

    expected = np.array([[[ i22, u22],   # 2,2
                          [ i23, u23],   # 2,3
                          [ i24, u24]],  # 2,4
                         [[ i32, u32],   # ...
                          [ i33, u33],
                          [ i34, u34]],  # 3,4
                         [[ i42, u42],   # ...
                          [ i43, u43],
                          [ i44, u44]]]) # 4,4

    # Note: we're comparing float value here
    assert np.all(np.isclose( pixel_count, expected ))

def test_union_intersection_count_two_maps_more_labels_in_pred():
    """
    Provided two label maps that each encode (potentially overlapping) polygons, yield 
    intersection and union counts for each possible pair of labels (i,j) with i ∈  map1
    and j ∈ map2.
    Shared pixels in each map (i.e. overlapping polygons) are counted independently for each polygon.
    The metrics function should deal correctly with GT labels that are missing in the predicted map.
    """
    # Pred. labels: 2,3,4,5
    map1 = seglib.array_to_rgba_uint8(np.array(
                     [[2,2,2,0,0,0],
                      [2,2,2,0,0,0],
                      [2,2,0x20304,0x304,4,0],
                      [0,0x502,0x304,0x304,0x304,4],
                      [5,0x405,4,4,4,0], 
                      [0,0,4,0x402,0,0]], dtype='int32'))

    # GT labels: 2,3,4
    map2 = seglib.array_to_rgba_uint8(np.array(
                     [[0,2,2,0,0,0],
                      [2,2,4,2,2,0],
                      [2,2,0x20304,0x304,4,0],
                      [0,3,0x304,0x304,0x304,4],
                      [0,0,3,4,4,0],
                      [0,0,0x204,4,0,0]], dtype='int32'))

    pixel_count = seglib.polygon_pixel_metrics_two_maps( map1, map2 )[:,:,:2]

    c2l, c2r = 8+1/3+.5*2, 8+1/3+.5
    c3l, c3r = 1/3+.5*4, 1/3+2+.5*4
    c4l, c4r = 1/3+6*.5+6, 1/3+5*.5+6
    c5l, c5r = 1+2*.5, 0
    i22, i23, i24 = 6+1/3, 1/3+.5, 1+1/3+.5
    i32, i33, i34 = 1/3, 1/3+.5*4, 1/3+.5*4
    i42, i43, i44 = 1/3+.5, 1/3+.5*4+1, 1/3+.5*6+4
    i52, i53, i54 = 0, .5, 0
    u22, u23, u24 = c2l+c2r-i22, c2l+c3r-i23, c2l+c4r-i24
    u32, u33, u34 = c3l+c2r-i32, c3l+c3r-i33, c3l+c4r-i34
    u42, u43, u44 = c4l+c2r-i42, c4l+c3r-i43, c4l+c4r-i44
    u52, u53, u54 = c5l+c2r-i52, c5l+c3r-i53, c5l+c4r-i54

    #print("\n"+repr( pixel_count ))
    expected =    np.array([[[ i22, u22],   # 2,2
                             [ i23, u23],   # 2,3
                             [ i24, u24]],  # 2,4
                            [[ i32, u32],   # ...
                             [ i33, u33],
                             [ i34, u34]],  # 3,4
                            [[ i42, u42],   # ...
                             [ i43, u43],
                             [ i44, u44]],
                            [[ i52, u52],   # ...
                             [ i53, u53],
                             [ i54, u54]]]) # 4,4
    #print("\n"+repr(expected))

    # Note: we're comparing float value here
    assert np.all(np.isclose( pixel_count, expected ))

def test_union_intersection_count_two_maps_more_labels_in_GT():
    """
    Provided two label maps that each encode (potentially overlapping) polygons, yield 
    intersection and union counts for each possible pair of labels (i,j) with i ∈  map1
    and j ∈ map2.
    Shared pixels in each map (i.e. overlapping polygons) are counted independently for each polygon.
    The metrics function should deal correctly with GT labels that are missing in the predicted map.
    """
    # Pred. labels: 2,3,4
    map1 = seglib.array_to_rgba_uint8(np.array( 
                     [[0,2,2,0,0,0],
                      [2,2,4,2,2,0],
                      [2,2,0x20304,0x304,4,0],
                      [0,3,0x304,0x304,0x304,4],
                      [0,0,3,4,4,0],
                      [0,0,0x204,4,0,0]], dtype='int32'))

    # GT labels: 2,3,4,5
    map2 = seglib.array_to_rgba_uint8(np.array(
                     [[2,2,2,0,0,0],
                      [2,2,2,0,0,0],
                      [2,2,0x20304,0x304,4,0],
                      [0,0x502,0x304,0x304,0x304,4],
                      [5,0x405,4,4,4,0], 
                      [0,0,4,0x402,0,0]], dtype='int32'))

    pixel_count = seglib.polygon_pixel_metrics_two_maps( map1, map2 )[:,:,:2]

    c2l, c2r = 8+1/3+.5, 8+1/3+.5*2
    c3l, c3r = 1/3+2+.5*4, 1/3+.5*4
    c4l, c4r = 1/3+5*.5+6, 1/3+6*.5+6
    c5l, c5r = 0, 1+2*.5
    i22, i23, i24, i25 = 6+1/3, 1/3, 1/3+.5, 0
    i32, i33, i34, i35 = 1/3+.5, 1/3+.5*4, 1/3+.5*4+1, .5
    i42, i43, i44, i45 = 1+1/3+.5, 1/3+.5*4, 1/3+.5*6+4, 0
    u22, u23, u24, u25 = c2l+c2r-i22, c2l+c3r-i23, c2l+c4r-i24, c2l+c5r-i25
    u32, u33, u34, u35 = c3l+c2r-i32, c3l+c3r-i33, c3l+c4r-i34, c3l+c5r-i35
    u42, u43, u44, u45 = c4l+c2r-i42, c4l+c3r-i43, c4l+c4r-i44, c4l+c5r-i45

    #print("\n"+repr( pixel_count ))
    expected =    np.array([[[ i22, u22],  # 2,2
                             [ i23, u23],  # 2,3
                             [ i24, u24],  # 2,4
                             [ i25, u25]], # 2,5
                            [[ i32, u32],  # ...
                             [ i33, u33],
                             [ i34, u34],
                             [ i35, u35]], # 3,5
                            [[ i42, u42],  # ...
                             [ i43, u43],
                             [ i44, u44],
                             [ i45, u45]]])
    #print("\n"+repr(expected))

    # Note: we're comparing float value here
    assert np.all(np.isclose( pixel_count, expected ))

def test_precision_recall_two_maps():
    """
    Provided two label maps that each encode (potentially overlapping) polygons, yield 
    intersection and union counts for each possible pair of labels (i,j) with i ∈  map1
    and j ∈ map2.
    Shared pixels in each map (i.e. overlapping polygons) are counted independently for each polygon.
    """
    # map1 (_l_)  = Pred, map2 (_r_) = GT
    map1 = seglib.array_to_rgba_uint8(np.array([[2,2,2,0,0,0],
                      [2,2,2,0,0,0],
                      [2,2,0x20304,0x304,4,0],
                      [0,0,0x304,0x304,0x304,4],
                      [0,0,4,4,4,0],
                      [0,0,4,0x402,0,0]], dtype='int32'))

    map2 = seglib.array_to_rgba_uint8(np.array( [[0,2,2,0,0,0],
                      [2,2,4,2,2,0],
                      [2,2,0x20304,0x304,4,0],
                      [0,3,0x304,0x304,0x304,4],
                      [0,0,3,4,4,0],
                      [0,0,0x204,4,0,0]], dtype='int32'))

    metrics = seglib.polygon_pixel_metrics_two_maps( map1, map2 )
    intersection_union, precision_recall = metrics[:,:,:2], metrics[:,:,2:]

    c2l, c2r = 8+1/3+.5, 8+1/3+.5
    c3l, c3r = 1/3+.5*4, 1/3+2+.5*4
    c4l, c4r = 1/3+5*.5+6, 1/3+5*.5+6
    i22, i23, i24 = 6+1/3, 1/3, 1+1/3+.5
    i32, i33, i34 = 1/3, 1/3+.5*4, 1/3+.5*4
    i42, i43, i44 = 1/3+.5, 1/3+.5*4+1, 1/3+.5*6+4
    u22, u23, u24 = c2l+c2r-i22, c2l+c3r-i23, c2l+c4r-i24
    u32, u33, u34 = c3l+c2r-i32, c3l+c3r-i33, c3l+c4r-i34
    u42, u43, u44 = c4l+c2r-i42, c4l+c3r-i43, c4l+c4r-i44

    expected_intersection_union = np.array(
                        [[[ i22, u22],   # 2,2
                          [ i23, u23],   # 2,3
                          [ i24, u24]],  # 2,4
                         [[ i32, u32],   # ...
                          [ i33, u33],
                          [ i34, u34]],  # 3,4
                         [[ i42, u42],   # ...
                          [ i43, u43],
                          [ i44, u44]]]) # 4,4

    expected = np.array([[[ i22/c2l, i22/c2r],   # 2,2
                          [ i23/c2l, i23/c3r],   # 2,3
                          [ i24/c2l, i24/c4r]],  # 2,4
                         [[ i32/c3l, i32/c2r],   # ...
                          [ i33/c3l, i33/c3r],
                          [ i34/c3l, i34/c4r]],  # 3,4
                         [[ i42/c4l, i42/c2r],   # ...
                          [ i43/c4l, i43/c3r],
                          [ i44/c4l, i44/c4r]]]) # 4,4

    # Note: we're comparing float value here
    assert np.all(np.isclose( intersection_union, expected_intersection_union, 1e-4 ))
    assert np.all(np.isclose( precision_recall, expected, 1e-4 ))

def test_get_polygon_pixel_metrics_wrong_pred_type():
    """
    First map should be a 4-channel tensor
    """
    map1 = torch.tensor([[2,2,2,0,0,0],
                         [2,2,2,0,0,0],
                         [2,2,0x20304,0x304,4,0],
                         [0,0,0x304,0x304,0x304,4],
                         [0,0,4,4,4,0],
                         [0,0,4,0x402,0,0]], dtype=torch.int)

    map2 = torch.tensor([[[0, 2, 2, 0, 0, 0],
                          [2, 2, 4, 2, 2, 0],
                          [2, 2, 4, 4, 4, 0],
                          [0, 3, 4, 4, 4, 4],
                          [0, 0, 3, 4, 4, 0],
                          [0, 0, 4, 4, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 3, 3, 0, 0],
                          [0, 0, 3, 3, 3, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 2, 0, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 2, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]]], dtype=torch.uint8)

    with pytest.raises( TypeError ):
        seglib.polygon_pixel_metrics_from_polygon_maps_and_mask(map1,map2)

def test_get_polygon_pixel_metrics_wrong_gt_type():
    """
    Second map should be a 4-channel tensor
    """

    map1 = torch.tensor([[[0, 2, 2, 0, 0, 0],
                          [2, 2, 4, 2, 2, 0],
                          [2, 2, 4, 4, 4, 0],
                          [0, 3, 4, 4, 4, 4],
                          [0, 0, 3, 4, 4, 0],
                          [0, 0, 4, 4, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 3, 3, 0, 0],
                          [0, 0, 3, 3, 3, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 2, 0, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 2, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]]], dtype=torch.uint8)

    map2 = torch.tensor([[2,2,2,0,0,0],
                         [2,2,2,0,0,0],
                         [2,2,0x20304,0x304,4,0],
                         [0,0,0x304,0x304,0x304,4],
                         [0,0,4,4,4,0],
                         [0,0,4,0x402,0,0]], dtype=torch.int)

    with pytest.raises( TypeError ):
        seglib.polygon_pixel_metrics_from_polygon_maps_and_mask(map1,map2)


def test_get_polygon_pixel_metrics_different_map_shapes():
    """
    On an actual, only a few sanity checks for testing
    """
    map1 = torch.tensor([[[2, 2, 2, 0, 0, 0],
                          [2, 2, 2, 0, 0, 0],
                          [2, 2, 4, 4, 4, 0],
                          [0, 0, 4, 4, 4, 4],
                          [0, 0, 4, 2, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 3, 3, 0, 0],
                          [0, 0, 3, 3, 3, 0],
                          [0, 0, 0, 4, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 2, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]]], dtype=torch.uint8)

    map2 = torch.tensor([[[0, 2, 2, 0, 0, 0],
                          [2, 2, 4, 2, 2, 0],
                          [2, 2, 4, 4, 4, 0],
                          [0, 3, 4, 4, 4, 4],
                          [0, 0, 3, 4, 4, 0],
                          [0, 0, 4, 4, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 3, 3, 0, 0],
                          [0, 0, 3, 3, 3, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 2, 0, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 2, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]],
                         [[0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]]], dtype=torch.uint8)

    with pytest.raises( TypeError ):
        seglib.polygon_pixel_metrics_from_polygon_maps_and_mask(map1,map2)


def test_get_polygon_pixel_metrics_from_maps_and_mask_small_image(  data_path ):
    """
    On an actual image, with polygons loaded from serialized tensors, only a few sanity checks for testing
    """

    polygon_pred = torch.load(str(data_path.joinpath('segdict_NA-ACK_14201223_01485_r-r1+model_20_reduced.pt')))
    polygon_gt = torch.load(str(data_path.joinpath('NA-ACK_14201223_01485_r-r1_reduced.pt')))
    binary_mask = torch.load(str(data_path.joinpath('NA-ACK_14201223_01485_r-r1_reduced_binarized.pt')))

    metrics = seglib.polygon_pixel_metrics_from_polygon_maps_and_mask(polygon_pred, polygon_gt, binary_mask)

    assert metrics.dtype == np.float32 
    assert np.all( metrics[:,:,0].diagonal() != 0 ) # intersections
    assert np.all( metrics[:,:,1] != 0 ) # unions

def test_get_polygon_pixel_metrics_from_img_json(  data_path ):
    """
    On an actual image, with polygon loaded from JSON dictionaries, only a few sanity checks for testing
    """
    input_img = Image.open( data_path.joinpath('NA-ACK_14201223_01485_r-r1_reduced.png'))
    dict_pred = json.load( open(data_path.joinpath('segdict_NA-ACK_14201223_01485_r-r1+model_20_reduced.json'), 'r'))
    dict_gt = json.load( open(data_path.joinpath('NA-ACK_14201223_01485_r-r1_reduced.json'), 'r'))

    metrics = seglib.polygon_pixel_metrics_from_img_json(input_img, dict_pred, dict_gt)

    assert metrics.dtype == np.float32 
    assert np.all( metrics[:,:,0].diagonal() != 0 ) # intersections
    assert np.all( metrics[:,:,1] != 0 ) # unions

@pytest.mark.fail_slow('30s')
@pytest.mark.parametrize("distance", [2, 7])
def test_polygon_pixel_metrics_from_full_charter(  data_path, distance ):
    """
    On an full page, with polygons loaded from serialized tensors, only a few sanity checks for testing.
    + Crude check for performance for a couple of label distance.
    """
    polygons_pred = torch.load(str(data_path.joinpath('segdict_NA-ACK_14201223_01485_r-r1+model_20.pt')))
    polygons_gt = torch.load(str(data_path.joinpath('NA-ACK_14201223_01485_r-r1.pt')))
    binary_mask = torch.load(str(data_path.joinpath('NA-ACK_14201223_01485_r-r1_binarized.pt')))

    # for any polygon label in predicted map, counting intersections with GT map for labels in [l-d .. l+2d]
    metrics = seglib.polygon_pixel_metrics_from_polygon_maps_and_mask(polygons_pred, polygons_gt, binary_mask, label_distance=distance)
    assert metrics.dtype == np.float32 
    # union counts should never be 0
    assert np.all( metrics[:,:,1] != 0 )

def test_polygon_pixel_metrics_to_line_based_scores():
    """
    On an actual image, a sanity check on the diagonal values.
    """
    metrics = np.array([[[ 6.3333335 , 11.833334  ,  0.7169811 ,  0.67857146],
                         [ 0.33333334, 10.833334  ,  0.03773585,  0.14285713],
                         [ 0.8333334 , 17.333334  ,  0.09433962,  0.08928571],
                         [ 0.        , 10.833334  ,  0.        ,  0.        ]],
                        [[ 0.8333334 , 12.833333  ,  0.1923077 ,  0.08928572],
                         [ 2.3333335 ,  4.3333335 ,  0.53846157,  1.        ],
                         [ 3.3333335 , 10.333334  ,  0.7692308 ,  0.35714284],
                         [ 0.5       ,  5.8333335 ,  0.11538461,  0.25      ]],
                        [[ 1.8333334 , 16.333334  ,  0.20754716,  0.19642858],
                         [ 2.3333335 ,  8.833334  ,  0.26415095,  1.        ],
                         [ 7.3333335 , 10.833334  ,  0.83018863,  0.78571427],
                         [ 0.        , 10.833334  ,  0.        ,  0.        ]]],
                        dtype=np.float32)

    assert seglib.polygon_pixel_metrics_to_line_based_scores(metrics, .1) == (2., 0.0, 1.0 , 2.0/3, 0.8)
    assert seglib.polygon_pixel_metrics_to_line_based_scores(metrics, .5) == (1.0, 2.0, 2.0, 0.2, 1.0/3)
    assert seglib.polygon_pixel_metrics_to_line_based_scores( metrics, .9) == (0.0, 3.0, 3.0, 0.0, 0.0)


def test_polygon_pixel_metrics_to_line_based_scores_full_charter(  data_path ):
    """
    On an actual image, a sanity check
    """
    metrics = torch.load(str(data_path.joinpath('full_charter_metrics.pt')))

    scores = seglib.polygon_pixel_metrics_to_line_based_scores( metrics, .6 )
    assert scores[-1] >= .8 

def test_polygon_pixel_metrics_to_pixel_based_scores_full_charter(  data_path ):
    """
    On an actual image, a sanity check
    """
    metrics = torch.load(str(data_path.joinpath('full_charter_metrics.pt')))

    scores = seglib.polygon_pixel_metrics_to_pixel_based_scores( metrics, .6 )
    assert scores[0] > .25
    assert scores[1] > .5 


def test_map_to_depth():
    """
    Provided a polygon map with compound pixels (intersections), the matrix representing
    the depth of each pixel should have 1 for 1-polygon pixels, 2 for 2-polygon pixels, etc.
    """
    map_hw = seglib.array_to_rgba_uint8(np.array([[2,2,2,0,0,0],
                           [2,2,2,0,0,0],
                           [2,2,0x20304,0x304,4,0],
                           [0,0,0x304,0x304,0x304,4],
                           [0,0,4,4,4,0],
                           [0,0,4,4,0,0]], dtype='int32'))

    depth_map = seglib.map_to_depth( map_hw )

    assert torch.equal(
        depth_map,
        torch.tensor([[1,1,1,1,1,1],
                      [1,1,1,1,1,1],
                      [1,1,3,2,1,1],
                      [1,1,2,2,2,1],
                      [1,1,1,1,1,1],
                      [1,1,1,1,1,1]], dtype=torch.int))

def test_pagexml_to_segmentation_dict(  data_path ):
    """
    Conversion between PageXML segmentation output and JSON/Python dictionary should keep the lines.
    """
    pagexml = str(data_path.joinpath('NA-ACK_14201223_01485_r-r1_reduced.xml'))

    segdict = seglib.pagexml_to_segmentation_dict( pagexml )

    assert len(segdict['lines']) == 4
    assert [ l['line_id'] for l in segdict['lines'] ] == ['r1l1', 'r1l2', 'r1l3', 'r1l4'] 
    assert [ len(l['baseline']) for l in segdict['lines'] ] == [21, 21, 21, 21] 


@pytest.mark.parametrize(
        'label,expected',[
            (0, [0]), 
            (255, [255]),
            (3, [3]), 
            (0x302, [3,2]), 
            (0x203, [2,3]),
            (0x40205, [4,2,5]),
            (0x1ffffff,[]),
            ])
def test_recover_labels_from_map_value_single_polygon(  label, expected ):
    assert seglib.recover_labels_from_map_value( label ) == expected




