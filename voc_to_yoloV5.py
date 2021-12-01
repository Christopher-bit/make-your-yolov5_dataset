import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
import numpy as np

# 数据标签
classes = ['armor', 'car']


def convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    if w >= 1:
        w = 0.99
    if h >= 1:
        h = 0.99
    return (x, y, w, h)


def convert_point_center(box):
    x = (box[0] + box[1])/2.0-1
    y = (box[2] + box[3])/2.0-1
    return (x, y)


def convert_annotation(rootpath, xmlname):
    xmlpath = rootpath + '/robomaster_Central China Regional Competition/image_annotation'
    xmlfile = os.path.join(xmlpath, xmlname)
    with open(xmlfile, "r", encoding='UTF-8') as in_file:
        txtname = xmlname[:-4]+'.txt'
        print(txtname)
        txtpath = rootpath + '/worktxt'  # 生成的.txt文件会被保存在worktxt目录下
        if not os.path.exists(txtpath):
            os.makedirs(txtpath)
        txtfile = os.path.join(txtpath, txtname)
        with open(txtfile, "w+", encoding='UTF-8') as out_file:
            tree = ET.parse(in_file)
            root = tree.getroot()
            size = root.find('size')
            w = int(size.find('width').text)
            h = int(size.find('height').text)
            out_file.truncate()
            i = 0
            j = 0
            armor_class = [[0 for r in range(3)] for s in range(30)]
            car_class = [[0 for r in range(4)] for s in range(10)]
            for obj in root.iter('object'):  # 对文件进行遍历，找到armor和car两个object，对其进行处理和暂存
                cls = obj.find('name').text
                if cls == 'armor':
                    armor_color = obj.find('armor_color').text
                    xmlbox = obj.find('bndbox')
                    b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(
                        xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                    x, y = convert_point_center(b)  # 得到装甲板中心坐标

                    if(armor_color == 'red'):
                        # 0,x,y    将装甲板中心坐标和代表颜色的编号暂存：红色
                        armor_class[i] = (0, x, y)
                        # print(armor_class[i])
                        i += 1  # i最后的数值就是armor的个数
                    if(armor_color == 'blue'):
                        # 1,x,y    将装甲板中心坐标和代表颜色的编号暂存：蓝色
                        armor_class[i] = (1, x, y)
                        # print(armor_class[i])
                        i += 1
                    if(armor_color == 'grey'):
                        # 2,x,y    将装甲板中心坐标和代表颜色的编号暂存：灰色
                        armor_class[i] = (2, x, y)
                        # print(armor_class[i])
                        i += 1

                elif cls == 'car':
                    cls_id = classes.index(cls)
                    xmlbox = obj.find('bndbox')
                    b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(
                        xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                    # x_min,y_min,x_max,y_max 将车辆左上和右下角点坐标暂存至car_class
                    car_class[j] = b
                    j += 1
            # print(armor_class)
            # for d,s,k in armor_class:
            #    print('armor: '+str(d)+' '+str(s)+' '+str(k))
            for x_min, x_max, y_min, y_max in car_class:
                if(x_min == 0 and x_max == 0):
                    break
                #print('car: '+str(x_min)+ " " +str(x_max)+ " " +str(y_min)+ " " +str(y_max))
                for color, x, y in armor_class:
                    #print('armor: '+str(color)+' '+str(x)+str(y))
                    if(x == 0 and y == 0):
                        break
                    # 如果某个装甲板在当前的车ROI里，即找到了当前车的颜色
                    if(x >= x_min and x <= x_max and y >= y_min and y <= y_max):
                        #print('\nfound proper box\n')
                        # 这时再将角点坐标转换为中心坐标和长宽
                        bb = convert((w, h), (x_min, x_max, y_min, y_max))
                        # 将类别名、中心坐标、长、宽输出至文件，保存为yolov5格式
                        out_file.write(str(color) + " " +
                                       " ".join([str(a) for a in bb]) + '\n')
                        break


if __name__ == "__main__":
    rootpath = '/home/chris/datasets/DJI ROCO'
    xmlpath = rootpath+'/robomaster_Central China Regional Competition/image_annotation'
    list = os.listdir(xmlpath)
    for i in range(0, len(list)):
        path = os.path.join(xmlpath, list[i])
        if ('.xml' in path) or ('.XML' in path):
            convert_annotation(rootpath, list[i])
            print('done', i)
        else:
            print('not xml file', i)
