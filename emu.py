#Thanks to ttom795's open source Chippure emulator, I observed some code there to get a better understanding of what I need to do
#also, thanks to https://www.freecodecamp.org/news/creating-your-very-own-chip-8-emulator/, great reference
#+, thanks to r/EmuDev discord, more specifically calc84maniac#7184, I spent 5 hours trying to figure out why sprite draw didn't work only to figure out it was a one line indentation error :P
from tkinter import *
import math
import time
import random
import sys
import json

#screen
cols = 64
rows = 32
scale = 4

screen = Tk()
screen.title('Test with screens')
screen.geometry(str(cols*scale)+'x'+str(rows*scale))
screen.config(bg='#000000')

canvas = Canvas(screen,bg="#000000")

keypressed = None

def inputEventDown(event):
  global cycle
  global keypressed
  #print("keypress")
  keys = {
    "1":0x1,
    "2":0x2,
    "3":0x3,
    "4":0xc,
    "q":0x4,
    "w":0x5,
    "e":0x6,
    "r":0xD
  }
  if event.char == " ":
    if cycle:
      cycle = False
    else:
      cycle = True
      emuloop()
  elif keys[event.char]:
    keypressed = keys[event.char]
    print(keypressed)

def inputEventUp(event):
  global cycle
  global keypressed
  keys = {
    "1":0x1,
    "2":0x2,
    "3":0x3,
    "4":0xc,
    "q":0x4,
    "w":0x5,
    "e":0x6,
    "r":0xD
  }
  if keys[event.char] == keypressed:
    keypressed = None
    print("keyup")

def drawPixel(x, y): #col is x row is y
  canvas.create_rectangle(
    x*scale, y*scale, (x*scale)+scale, (y*scale)+scale,
    fill="white",
    tag="squa"
    )
  canvas.pack()
  screen.update()

def cls():
  canvas.delete('all')
  
def excopcode(opcode):
  global pc
  global stack
  global v
  global selfi
  global cycle
  pc += 2

  x = (opcode & 0x0F00) >> 8
  #x - A 4-bit value, the lower 4 bits of the high byte of the instruction
  y = (opcode & 0x00F0) >> 4
  #y - A 4-bit value, the upper 4 bits of the low byte of the instruction
  code = (opcode & 0xF000)
  #to check code without nnn
  kk = (opcode & 0xFF)
  #kk or byte - An 8-bit value, the lowest 8 bits of the instruction

  
  
  print("executing " + str(hex(opcode)))
  if code == 0x0000:
    if opcode == 0x00E0: #cls
      cls()
      print("cleared screen" + str(hex(opcode)) + str(opcode))
    if opcode == 0x00EE: #return (pop from stack, store in pc)
      pc = stack.pop()
      print("popped")
  elif code == 0x1000: #JP addr
    #0xFFF is nnn,
    #ex 0x1426 & 0xFFF would give us 0x426 for 0xFFF
    #This SHOULD be pc = (opcode & 0xFFF)
    #However instead I'm going to make it stop the cycle since it will be an infinite loop without rendering anything, yeah I think something might be wrong with how I update my render but psh I'll get to that later
    #cycle = False
    pc = (opcode & 0xFFF)

  elif code == 0x2000:
    stack.append(pc)
    pc = (opcode & 0xFFF)

  elif code == 0x3000:
    if v[x] == kk:
        pc += 2

  elif code == 0x4000:
    if v[x] != kk:
      pc += 2
      
  elif code == 0x5000:
    if v[x] == v[y]:
      pc += 2

  elif code == 0x6000: #LD Vx, byte
    v[x] = kk
    
  
  elif code == 0x7000: #ADD Vx, byte
    v[x] += kk

  elif code == 0x8000:
    e = (opcode & 0xF)
    if e == 0x0:
      v[x] = v[y];
    elif e == 0x1:
      v[x] |= v[y]
    elif e == 0x2:
      v[x] &= v[y]
    elif e == 0x3:
      v[x] ^= v[y]
    elif e == 0x4:
      sum = v[x] + v[y]
      v[0xF] = 0
      if sum > 0xFF:
        v[0xF] = 1;
      v[x] = sum
    elif e == 0x5:
      v[0xF] = 0
      if (v[x] > v[y]):
        v[0xF] = 1
      v[x] -= v[y]
    elif e == 0x6:
      v[0xF] = (v[x] & 0x1)
      v[x] >>= 1
    elif e == 0x7:
      v[0xF] = 0
      if (v[y] > v[x]):
        v[0xF] = 1
      v[x] = v[y] - v[x]
    elif e == 0xE:
      v[0xF] = (v[x] & 0x80)
      v[x] <<= 1
      
  elif code == 0x9000:
    if v[x] != v[y]:
      pc += 2
    
  elif code == 0xA000:
    selfi = opcode & 0xFFF
    
  elif code == 0xB000:
    pc = (opcode & 0xFFF) + v[0]

  elif code == 0xC000:
    rand = random.randint(0, 255)
    v[x] = rand & (opcode & 0xFF)
    
  elif code == 0xD000: #DRW Vx, Vy, nibble
    width = 8
    height = (opcode & 0xF)
    v[0xF] = 0
    for row in range(height):
      sprite = memory[selfi+row]
      for col in range(width):
        if (sprite & 0x80) > 0:
          if drawPixel(v[x]+col, v[y]+row):
            v[0xF] = 1
        sprite <<= 1

  elif code == 0xE000:
    if kk == 0x9E:
      if keypressed == v[x]:
        pc += 2
    elif kk == 0xA1:
      if keypressed != v[x]:
        pc += 2
    
  elif code == 0xF000:
    if kk == 0x0A:
      cycle = False
      print("paused by 0x0A")
    elif kk == 0x1E: #LD Vx, DT
      selfi += v[x]
    elif kk == 0x29:
      selfi = v[x]*0x5
    elif kk == 0x33:
      memory[selfi] = int(v[x] / 100)
      memory[selfi + 1] = int((v[x] % 100) / 10)
      memory[selfi + 2] = int(v[x] % 10)
    elif kk == 0x55:
      registerIndex = 0
      while registerIndex <= x:
        memory[selfi + registerIndex] = v[registerIndex]
        registerIndex += 1
    elif kk == 0x65:
      registerIndex = 0
      while registerIndex <= x:
        v[registerIndex] = memory[selfi + registerIndex]
        registerIndex += 1
  else:
    print("unknown opcode: "+ opcode)

def emuloop():
  global cycle
  while cycle:
    daopcode = memory[pc] << 8 | memory[pc+1]
    print(pc)
    excopcode(daopcode)

memory = [0x0 for i in range(4096)]
filename = input("Input rom name: ") + ".ch8"
#filename = "invaders.ch8"
dafile = open(filename, 'rb')
program = dafile.read()
dafile.close()
pc = 0x200
stack = []
v = [0x0 for i in range(16)] # 16 8-bit registers
selfi = 0 #Stores memory addresses. Set this to 0 since we aren't storing anything at initialization.
cycle = True
screen.bind('<Key>',inputEventDown)
screen.bind('<KeyRelease>',inputEventUp)
for i in range(len(program)):
  memory[0x200+i] = program[i]
emuloop()
