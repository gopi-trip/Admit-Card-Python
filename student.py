import csv
from PIL import Image,ImageDraw,ImageFont
import gdown
def admitCard(name,branch,enrollment,course,subjectDict,subjectCodes,url,year,semester,dateDict,time):
        #Creating an image
        width = 1375
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
        url = url
        out = f"images/{fileName}.png"
        gdown.download(url,out,fuzzy=True)
        
        name = "Name: " + name
        branch = "Branch: " + branch
        enrollment = "Enrollment No: " + enrollment 
        course = "Course: " + course
        year = "Year: " + year
        semester = "Semester: " + semester
        time = time
        drawing_context.text((480,10),text=headerText,font=font1,fill="black")
        drawing_context.text((0 ,20),text='_'*width,font=font1,fill=(0,0,0))
        drawing_context.text((580,65),text=titleText,font=font1,fill=(0,0,0))
        
        rect_x_start = 10
        rect_x_end = width - 10
        up_rect_y_start = 110
        up_rect_y_end = up_rect_y_start + 240
        low_rect_y_start = up_rect_y_end + 20
        low_rect_y_end = height-75
        
        drawing_context.rectangle([(rect_x_start,up_rect_y_start),(rect_x_end,350)],outline="black",width=2)
        drawing_context.rectangle([(rect_x_start,low_rect_y_start),(rect_x_end,low_rect_y_end)],outline="black",width=2)
        
        text_x=24
        text_y=150
        
        drawing_context.text((text_x,text_y),text=name,font=font2,fill=(0,0,0))
        drawing_context.text((len(name)*20+text_x,text_y),text=year,font=font2,fill=(0,0,0))
        
        text_y+=50
        drawing_context.text((text_x,text_y),text=enrollment,font=font2,fill=(0,0,0))
        drawing_context.text((len(enrollment)*15+text_x,text_y),text=semester,font=font2,fill=(0,0,0))
        
        text_y+=50
        
        drawing_context.text((text_x,text_y),text=branch,font=font2,fill=(0,0,0))
        drawing_context.text((len(branch)*15+text_x,text_y),text=course,font=font2,fill=(0,0,0))
        
        #Subjects
        
        x=24
        y=394
        drawing_context.text((x,y),text="Subject",fill="black",font=font1)
        x = x + 340
        drawing_context.text((x,y),text="Subject Code",fill="black",font=font1)
        x = x + 370
        drawing_context.text((x,y),text="Date",fill="black",font=font1)
        x = x + 350
        drawing_context.text((x,y),text="Exam Time",fill="black",font=font1)
        
        line_x = 300
        line_y = y + 50
        
        drawing_context.line([(rect_x_start,line_y),(rect_x_end,line_y)],fill=128)
        
        sub_x = 20
        sub_y = 460
        
        for subject in subjectDict.values():
            drawing_context.text((sub_x,sub_y),text=subject,font=font2,fill="black")
            drawing_context.line([(10,sub_y+40),(width-10,sub_y+40)],fill=128)
            sub_y = sub_y + 60
        
        drawing_context.line([(line_x,low_rect_y_start),(line_x,low_rect_y_end)],fill=128)
        
        code_x = 410
        code_y = 460
        for value in subjectCodes.values():
            drawing_context.text((code_x,code_y),text=value,font=font2,fill="black")
            code_y = code_y + 60
        
        line_x = line_x + 320
        drawing_context.line([(line_x,low_rect_y_start),(line_x,low_rect_y_end)],fill=128)
        date_x = 730
        date_y = 458
        for value in dateDict.values():
            drawing_context.text((date_x,date_y),text=value,font=font2,fill="black")
            date_y = date_y + 59
        
        line_x = line_x + 355
        drawing_context.line([(line_x,low_rect_y_start),(line_x,low_rect_y_end)],fill=128)
        
        time_x = 1115
        time_y = 460
        for x in range(len(subjectList)):
            drawing_context.text((time_x,time_y),text=time,font=font2,fill="black")
            time_y = time_y + 59
        
        sig_x = 1150
        sig_y = height-110
        drawing_context.text((sig_x,sig_y),text="Signature",font=font2,fill="black")
        
        with Image.open(f"images/{fileName}.png") as img:  #Enter your image path
            img = img.resize((170,200))
            output.paste(img,(width-400,130))
        with Image.open(f"sig.jpg") as img:  #Enter your image path
            img = img.resize((100,30))
            output.paste(img,(sig_x,sig_y-40))
        
        output.save(f"images/Admit Card/output.{fileName}.pdf") #Enter path where you wish to save the files
        
        
with open('student_records_extended.csv','r') as f:
    reader = csv.DictReader(f)
    for line in reader:
        subjectList = line['Subjects'].split(",")
        subjectTuple = tuple(i for i in range(len(subjectList)))
        subjectDict = dict(zip(subjectTuple,subjectList))
        subjectCodeList = line['Subject Codes'].split(",")
        subjectCodeTuple = tuple(i for i in range(len(subjectCodeList)))
        subjectCodeDict = dict(zip(subjectCodeTuple,subjectCodeList))
        examDateList = line['Dates'].split(",")
        examDateTuple = tuple(i for i in range(len(examDateList)))
        examDateDict = dict(zip(examDateTuple,examDateList))
        # print(subjectDict)
        name = line['Name']
        course = line['Course']
        registrationNo = line['Registration No.']
        branch = line['Branch']
        imageUrl = line['Photo Link']
        year = line['Year']
        semester = line['Semester']
        time = line['Time']
        admitCard(name,branch,registrationNo,course,subjectDict,subjectCodeDict,imageUrl,year,semester,examDateDict,time)
   
        


     
