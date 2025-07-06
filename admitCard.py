from PIL import Image,ImageDraw,ImageFont
import os

class Student():
    heading = "ABC University of Technology"
    title = "ADMIT CARD"
    def __init__(self,name,enr,branch,course,subjects):
        self.name=name
        self.branch=branch
        self.enrollmentNo=enr
        self.course=course
        self.subjects = subjects
        
    def __repr__(self):
        return f"Student(Name='{self.name}',Branch='{self.branch}',Course='{self.course}',Subjects='{self.subjects}')"
    
    def admitCard(self):
        #Creating an image
        width = 600
        height=900
        output = Image.new(mode='RGB',size=(width,height),color=(255,255,255))
        
        #Get a font
        font2 = ImageFont.truetype('Roboto-VariableFont_wdth,wght.ttf',24)
        font1 = ImageFont.truetype('Roboto-VariableFont_wdth,wght.ttf',34)
        
        #Creating a drawing context
        drawing_context = ImageDraw.Draw(output);
        headerText = self.heading
        titleText = self.title
        
        name = "Name: " + self.name
        branch = "Branch: " + self.branch
        enrollment = "Enrollment No: " + self.enrollmentNo
        course = "Course: " + self.course
        
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
        for subject in self.subjects:
            drawing_context.text((sub_x,sub_y),text=subject,font=font2,fill="black")
            sub_y = sub_y + 60
        
        code_x = 410
        code_y = 460
        for value in self.subjects.values():
            drawing_context.text((code_x,code_y),text=value,font=font2,fill="black")
            code_y = code_y + 60
        
        with Image.open('peter.jpeg') as img:
            img = img.resize((150,200))
            output.paste(img,(width-200,135))
        
        output.show()

# peter.admitCard()
# print(student1)
# print(student2)
