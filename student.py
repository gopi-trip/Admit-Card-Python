import csv
from PIL import Image,ImageDraw,ImageFont
import os
import gdown
def admitCard(name,branch,enrollment,course,subjectDict,subjectCodes,url):
        #Creating an image
        width = 600
        height=900
        output = Image.new(mode='RGB',size=(width,height),color=(255,255,255))
        
        #Get a font
        font2 = ImageFont.truetype('Roboto-VariableFont_wdth,wght.ttf',24)
        font1 = ImageFont.truetype('Roboto-VariableFont_wdth,wght.ttf',34)
        
        #Creating a drawing context
        drawing_context = ImageDraw.Draw(output);
        headerText = "ABC University of Technology"
        titleText = "ADMIT CARD"
        fileName = name
        url = imageUrl
        out = f"images/{fileName}.png"
        gdown.download(url,out,fuzzy=True)
        
        name = "Name: " + name
        branch = "Branch: " + branch
        enrollment = "Enrollment No: " + enrollment 
        course = "Course: " + course
        
        drawing_context.text(((width - ((font1.size)*len(headerText))//2 - font1.size) ,10),text=headerText,font=font1,fill="black")
        drawing_context.text(((width - ((font1.size)*len(headerText))//2 - font1.size) ,30),text='------------------------------------------------',font=font1,fill=(0,0,0))
        drawing_context.text(((width - ((font1.size)*len(headerText))//2 + font1.size + 43.5),65),text=titleText,font=font1,fill=(0,0,0))
        drawing_context.text((14,150),text=name,font=font2,fill=(0,0,0))
        drawing_context.text((14,200),text=enrollment,font=font2,fill=(0,0,0))
        drawing_context.text((14,250),text=branch,font=font2,fill=(0,0,0))
        drawing_context.text((14,300),text=course,font=font2,fill=(0,0,0))
        
        #Subjects
        drawing_context.rectangle([(10,380),(width-10,860)],outline="black")
        x=24
        drawing_context.text((x,394),text="Subject",fill="black",font=font1)
        x = x + 350
        drawing_context.text((x,394),text="Subject Code",fill="black",font=font1)

        sub_x = 20
        sub_y = 460
        for subject in subjectDict.values():
            drawing_context.text((sub_x,sub_y),text=subject,font=font2,fill="black")
            sub_y = sub_y + 60
        
        code_x = 410
        code_y = 460
        for value in subjectCodes.values():
            drawing_context.text((code_x,code_y),text=value,font=font2,fill="black")
            code_y = code_y + 60
        
        with Image.open(f"images/{fileName}.png") as img:
            img = img.resize((150,200))
            output.paste(img,(width-200,135))
        
        
        output.save(f"images/Admit Card/output.{fileName}.pdf")
        
with open('student_records_extended.csv','r') as f:
    reader = csv.DictReader(f)
    for line in reader:
        subjectList = line['Subjects'].split(",")
        subjectTuple = tuple(i for i in range(len(subjectList)))
        subjectDict = dict(zip(subjectTuple,subjectList))
        subjectCodeList = line['Subject Codes'].split(",")
        subjectCodeTuple = tuple(i for i in range(len(subjectCodeList)))
        subjectCodeDict = dict(zip(subjectCodeTuple,subjectCodeList))
        # print(subjectDict)
        name = line['Name']
        course = line['Course']
        registrationNo = line['Registration No.']
        branch = line['Branch']
        imageUrl = line['Photo Link']
        admitCard(name,branch,registrationNo,course,subjectDict,subjectCodeDict,imageUrl)


     