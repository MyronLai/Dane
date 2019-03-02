import requests
import re


async def getCourses(subject, number):

    COURSE_URL = "https://www.albany.edu/cgi-bin/general-search/search.pl?USER=0009&DELIMITER=%5Ct&SUBST_STR=G%3AGraduate&SUBST_STR=U%3AUndergraduate&SUBST_STR=L%3ALab&SUBST_STR=D%3ADiscussion&SUBST_STR=S%3ASeminar&SUBST_STR=I%3AIndependent+Study&SUBST_STR=GRD%3AA-E&SUBST_STR=SUS%3ASatisfactory%2FUnsatisfactory&SUBST_STR=GLU%3ALoad+Credit+or+Unsatisfactory&SUBST_STR=GRU%3AResearch+Credit+or+Unsatisfactory&HEADING_FONT_FACE=Arial&HEADING_FONT_SIZE=3&HEADING_FONT_COLOR=black&RESULTS_PAGE_TITLE=&RESULTS_PAGE_BGCOLOR=%23F0F0F0&RESULTS_PAGE_HEADING=&RESULTS_PAGE_FONT_FACE=Arial&RESULTS_PAGE_FONT_SIZE=2&RESULTS_PAGE_FONT_COLOR=black&NO_MATCHES_MESSAGE=Sorry%2C+no+courses+were+found+that+match+your+criteria.&NO_PRINT=3&NO_PRINT=4&NO_PRINT=6&NO_PRINT=7&NO_PRINT=8&GREATER_THAN_EQ=26&NO_PRINT=26&Level=&College_or_School=&Department_or_Program=&Course_Subject=" + str(subject) + "&Course_Number=" + str(number) + "&Class_Number=&Course_Title=&Days=&Instructor=&Grading=&Course_Info=&Meeting_Info=&Comments=&Credit_Range=&Component_is_blank_if_lecture=&Topic_if_applicable=&Seats_remaining_as_of_last_update=&Session=&IT_Commons=&Fully_Online_Course=&General_Education_Course=&Honors_College_Course=&Writing_Intensive=&Oral_Discourse=&Info_Literacy=&Special_Restriction="
    
    COURSE_RESULTS = {
        "courses" : []
    }
    data = requests.get(COURSE_URL)
    RAW_COURSE_DATA = await stripHtmlTags(data.text)

    index = 0

    for currLine in RAW_COURSE_DATA:
        if currLine.startswith("Class Number"):
            COURSE_RESULTS['courses'].append({"class" : currLine.split(":  ")[1]})
        elif currLine.startswith("Course Info"):
            COURSE_RESULTS['courses'][index]['courseInfo'] = currLine.split(":  ")[1]
        elif currLine.startswith("Meeting"):
            COURSE_RESULTS['courses'][index]['meeting'] = currLine.split(": ")[1]

        elif currLine.startswith("Component"):
            isLab = currLine.split(": ")[1]
            if isLab == 'Lab':
                COURSE_RESULTS['courses'][index]['isLab'] = currLine.split(": ")[1]
            else:
                COURSE_RESULTS['courses'][index]['isLab'] = "Lecture"

        elif currLine.startswith("Seats"):
            COURSE_RESULTS['courses'][index]['seatsLeft'] = currLine.split("update: ")[1]
            index += 1

    return COURSE_RESULTS



async def stripHtmlTags(str):
    text = re.sub("<.*?>", " ", str)
    return text.strip().split("\n")
