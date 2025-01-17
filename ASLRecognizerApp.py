#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from VideoCapture import VideoCapture
import tkinter
import PIL.Image, PIL.ImageTk
import torchvision.transforms as tt
import cv2
import matplotlib.pyplot as plt

classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 
           'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 
           'W', 'X', 'Y', 'Z', 'del', 'nothing', 'space']



def fromImageToTensor(image):
    model_transform = tt.Compose([
                             tt.ToTensor(),
                             tt.Resize((224,224)),
                             tt.Normalize(mean=[0.485,0.485,0.485], std=[0.229,0.229,0.229]),
                         ])
    return model_transform(image)

def getModelPrediction(model, image):
    imageTensor = fromImageToTensor(image)
    imageTensor = imageTensor.reshape(1,3,224,224)
    response = model(imageTensor)
    _, predc = response.topk(1, 1, True, True)
    
    return classes[int(predc.numpy()[0])]

class ASLRecognizerApp:
    def __init__(self, window, window_title, model, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.model = model
        self.frame_iter = 0 
        self.max_frame_iter =10000  #Not to have too great numbers of fram iteration     
        self.video_source = video_source
        
        # Adding button to snap 
        self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snap)
        self.btn_snapshot.pack(anchor=tkinter.N, expand=True)

        self.middleFrame = tkinter.Frame(self.window)

        #Setting up the video capture
        self.setupVideoCapture()

        #Setting up the image documentation
        ASLDoc = self.loadImage("assets/ASLAlphabet.jpg", 700)
        self.labelAlphabet= tkinter.Label(self.middleFrame,image=ASLDoc)
        self.labelAlphabet.pack(side=tkinter.LEFT)
        
        self.middleFrame.pack()

        # Adding button to clear the text
        self.btn_snapshot=tkinter.Button(window, text="Clear", width=20, command=self.clearText)
        self.btn_snapshot.pack(anchor=tkinter.S)

        # Setting up the message display
        self.message=""
        self.textDisplay = tkinter.Text(window)
        self.textDisplay.pack(anchor= tkinter.S, expand=True)
        
        self.delay = 2
        self.update()
        
        self.window.mainloop()

    def setupVideoCapture(self):
        self.vid = VideoCapture(self.video_source)
        self.canvas = tkinter.Canvas(self.middleFrame, width = self.vid.width, height = self.vid.height)
        self.canvas.pack(side=tkinter.LEFT)
        
    def loadImage(self, path, height):
        image = PIL.Image.open(path)
        imwidth, imheight = image.size
        imageRatio = imwidth/imheight
        image = image.resize((int(imageRatio*height), height), PIL.Image.ANTIALIAS)
        image = PIL.ImageTk.PhotoImage(image)
        return image
        
    def setMessageDisplay(self):
        self.textDisplay.delete(1.0,"end")
        self.textDisplay.insert(1.0, self.message)
        
    def update(self):
        ret, frame,boundingBox = self.vid.get_frame()
        [X,Y,H,W]= boundingBox
        if ret:
            #display the rectangle to the frame
            start_point = (X, Y)
            end_point =(int(X+max(W,H)), int(Y+max(W,H)))
            frame = cv2.rectangle(frame,start_point, end_point, (0, 0, 255), 2)
            if (self.frame_iter%8==0):
                if((H!=0 or W!=0) and (X!=0 and Y!=0 and H!=self.vid.height and W!=self.vid.width)):
                    #Preventing negative X and Y
                    X=max(0,X)
                    Y=max(0,Y)

                    #Making the snaped image square and take into account the borders
                    cropSize = min(max(H,W), self.vid.width-X, self.vid.height -Y)
                    end_point =(int(X+cropSize), int(Y+cropSize))

                    #Draws a red rectangle when it is snaping
                    frame = cv2.rectangle(frame,start_point, end_point, (255, 0, 0), 3)
                    self.gestureDetection(frame[Y:int(Y+cropSize),X:int(X+cropSize)])
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0,0, anchor = tkinter.NW, image=self.photo)
            self.frame_iter+=1    
            if(self.frame_iter>self.max_frame_iter):
                self.frame_iter =0

        self.window.after(self.delay, self.update)

    def gestureDetection(self,frame):
            letter= getModelPrediction(self.model,frame)
            if(letter == "space"):
                self.message +=" "
            elif (letter == "del"):
                if(len(self.message)>0):
                    self.message = self.message[0:len(self.message)-1]
            elif (len(letter)==1):
                self.message+=letter 
            self.setMessageDisplay()

    def snap(self):
        ret, frame,boundingBox = self.vid.get_frame()
        if ret:
            self.gestureDetection(frame)
    def clearText(self):
        self.message=""
        self.setMessageDisplay()
            