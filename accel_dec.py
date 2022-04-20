import io
import os
import sys
import struct
import numpy as np

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

class Vector4:
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

class ByteData:
    def __init__(self, data):
        self.data = data

    def read(self, pos, size):
        return self.data[pos:(pos+size)]

    def to_float(self, pos):
        result = struct.unpack('f', self.read(pos, 4))
        return np.float32(result[0])

    def to_int(self, pos):
        return np.int32(int.from_bytes(self.read(pos, 4), 'little'))

    def to_uint16(self, pos):
        return np.uint16(int.from_bytes(self.read(pos, 2), 'little'))

    def to_char(self, pos):
        return np.uint8(int.from_bytes(self.read(pos, 1), 'little'))

class ColModel:
    def __init__(self, box, sphere, flags, alloc_flag, data):
        self.box = box
        self.sphere = sphere
        self.flags = flags
        self.alloc_flag = alloc_flag
        self.data = data

def read_int(file):
    value = file.read(4)
    return int.from_bytes(value, 'little')

def filesize(file):
    file.seek(0, 2)
    fsize = file.tell()
    file.seek(0, 0)
    return fsize

with io.open(f"{os.getcwd()}\{sys.argv[1]}", mode="rb") as colaccel:
    accel_size = filesize(colaccel)

    col_item_qt = read_int(colaccel)
    col_items = ByteData(colaccel.read(48*col_item_qt))

    sections_qt = read_int(colaccel)
    section_size = ByteData(colaccel.read(4*sections_qt))

    ipl_defs = ByteData(colaccel.read(0x3400))

    col_bounds_qt = read_int(colaccel)
    col_bounds = ByteData(colaccel.read(col_bounds_qt*24))

    ipl_item_qt = read_int(colaccel)
    ipl_item_cache = ByteData(colaccel.read(ipl_item_qt*20))

col_list = []
if col_item_qt > 0:
    bi = 0
    for i in range(col_item_qt):

        cube_data = [Vector3(), Vector3()]

        cube_data[0].x = col_items.to_float(bi)
        cube_data[0].y = col_items.to_float(bi+4)
        cube_data[0].z = col_items.to_float(bi+8)

        cube_data[1].x = col_items.to_float(bi+12)
        cube_data[1].y = col_items.to_float(bi+16)
        cube_data[1].z = col_items.to_float(bi+20)

        sphere_data = Vector4()

        sphere_data.x = col_items.to_float(bi+24)
        sphere_data.y = col_items.to_float(bi+28)
        sphere_data.z = col_items.to_float(bi+32)
        sphere_data.w = col_items.to_float(bi+36)

        col_flags = col_items.to_char(bi+44)

        allocation_flag = col_items.to_char(bi+41) & np.uint8(0xFE) | col_items.to_char(bi+45) & np.uint8(1)

        col_list.append(ColModel(box=cube_data, sphere=sphere_data, flags=col_flags, alloc_flag=allocation_flag, data=0))

        bi += 48

#os.path.splitext(sys.argv[1])[0] get's the name file given by arg and split extension(.bin)
with io.open(f"{os.getcwd()}\{os.path.splitext(sys.argv[1])[0]}_dump.txt", mode="w") as out:

    out.write("\n-------------------Collision accelerator dump---------------------\n")
    out.write(f"File size: {accel_size} Bytes")
    out.write(f"\nCollision items: {col_item_qt}")
    out.write(f"\nSections: {sections_qt}")
    out.write(f"\nCollision bounds: {col_bounds_qt}")
    out.write(f"\nIPL items: {ipl_item_qt}")
    out.write("\n---------------------------Collisions-----------------------------\n")

    for i in range(0, col_item_qt):
        out.write("cube")
        out.write(f" {col_list[i].box[0].x:f}")
        out.write(f" {col_list[i].box[0].y:f}")
        out.write(f" {col_list[i].box[0].z:f}")
        out.write(f" {col_list[i].box[1].x:f}")
        out.write(f" {col_list[i].box[1].y:f}")
        out.write(f" {col_list[i].box[1].z:f}")
        out.write("\n")

        out.write("sphere")
        out.write(f" {col_list[i].sphere.x:f}")
        out.write(f" {col_list[i].sphere.y:f}")
        out.write(f" {col_list[i].sphere.z:f}")
        out.write(f" {col_list[i].sphere.w:f}")
        out.write("\n")

        out.write(f"flags {col_list[i].flags}\n")
        out.write(f"alloc_flag {col_list[i].alloc_flag}\n")

    out.write("\n----------------------------Sections------------------------------\n")

    for i in range(sections_qt):
        out.write(f"Section {i+1} size: {section_size.to_int(i*4)}\n")

    out.write("\n-----------------------------Bounds-------------------------------\n")

    for i in range(col_bounds_qt):
        out.write("BoundData:")
        out.write(f" {col_bounds.to_float((i*24)+4):f}")
        out.write(f" {col_bounds.to_float((i*24)+8):f}")
        out.write(f" {col_bounds.to_float((i*24)+12):f}")
        out.write(f" {col_bounds.to_char((i*24)+16)}")
        out.write(f" {col_bounds.to_char((i*24)+17)}")
        out.write(f" {col_bounds.to_char((i*24)+18)}")
        out.write(f" {col_bounds.to_char((i*24)+19)}")
        out.write(f" {col_bounds.to_char((i*24)+20)}")
        out.write(f" {col_bounds.to_char((i*24)+21)}")
        out.write("\n")

    out.write("\n----------------------------IPL Items-----------------------------\n")

    for i in range(ipl_item_qt):
        out.write("IPL Item:")
        out.write(f" {ipl_item_cache.to_int(i*20):d}")
        out.write(f" {ipl_item_cache.to_int((i*20)+4):d}")
        out.write(f" {ipl_item_cache.to_int((i*20)+8):d}")
        out.write(f" {ipl_item_cache.to_int((i*20)+12):d}")
        out.write(f" {ipl_item_cache.to_int((i*20)+16):d}")
        out.write("\n")