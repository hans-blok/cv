# Functional design html-generator
# ( example ) means entity
# ` means data item
# / means initiate (or call) function
# & means END FUNCTION

The occurences of the entities are found in txt-files with the same name (except these are in lowercase)

Files have extention .txt and are found in folder content


/WRITE_SIDEBAR

DO FOR EACH b IN (BLOCKS)
    WRITE_LINE b.title (note: if empty no title is written )
    SEARCH_FILE filename=b.`name'
    IF b.`name` = "urls" THEN
       /write_urls_contact       
    ELSE b.`name` = "personal-data" THEN
       /write_personal_data
       WRITE_LINE light grey line
    ELSE b.`name` = "personal-text" THEN
       /write_personal-text
       WRITE_LINE light grey line
    ELSE b.`name` = "certifications" THEN
       /write_certifications
       WRITE_LINE light grey line
    ELSE `b.`name` = "education" THEN
       /write_educations
       WRITE_LINE light grey line
    ELSE b.`name` = "courses"
       /write_courses
       WRITE_LINE light grey line
    ELSE b.`name` = "courses-short" THEN
       /write_courses_short
       WRITE_LINE light grey line
    ELSE b.`name` = "engagements" THEN
       /write_engagements
       WRITE_LINE light grey line   
    END IF
END DO FOR EACH 
&

FUNCTION:write_sidebar
  SEARCH_FILE logo-header.jpg | logo-header.png
  WRITE "logo" 
  WRITE "Download PDF" button with link to cv.pdf
  /write_urls_contact
&    

FUNCTION:write_urls_contact
   DO FOR EACH u IN (urls)
    WRITE_TAG u "LinkedIn" with link to u.`linkedin_url`
    WRITE_TAG u "Website"  with link to u.`website_url`
    WRITE_TAG u "GitHub"   with link to u.`github_url`
    WRITE_TAG u `phone_nr`
    WRITE_TAG u ``e-mail`
END DO FOR EACH 
&

FUNCTION:write_personal_data
   DO FOR EACH p IN (PERSONAL-DATA)
    WRITE_TAG p p.`name`
    WRITE_TAG p p.`usual_name`
    WRITE_TAG p p.`place_of_residence`
    WRITE_TAG p p.`date_of_birth`
    WRITE_TAG p p.`job_title`
    WRITE_TAG p p.`job_title`
END DO FOR EACH 
SEARCH_FILE profile-photo.jpg OR profile-photo.png
WRITE_RIGHT "profile-photo.jpg" | "profile-photo.png"
&

FUNCTION:write_personal_text
  DO FOR THE instance in (PERSONAL-TEXT)
    WRITE_LINE `text_block_personal`    
  END DO  
&

FUNCTION:write_educations
  DO FOR EACH e IN instances in (EDUCATIONS)
    WRITE_LINE `e.period`, `e.name`,`e.place`
    WRITE_LINE `e.addition` outlined with `e.name`
    WRITE_LINE thin light grey line 
END DO
&

FUNCTION:write_certifications
  DO FOR EACH c IN  instances in (CERTIFCATIONS)
    WRITE_LINE `period`, `name`,`place`
    'addition placed under `name`
END DO
&

FUNCTION:write_courses
  DO FOR EACH c IN (COURSES)
    WRITE_LINE c.`year`, c.`name`, c.`learning_institute`
  END DO
&



FUNCTION:write_courses_short
  DO FOR THE instances in (COURSES-SHORT)
    WRITE_LINE `period`, `text_block_various_courses`
    WRITE_LINE `text_block placed` under `text_block_various_courses`
    where the text is wrapped and items are ended with a comma except the last one. 
  END DO  
&

FUNCTION:write_engagements
  DO FOR EACH f IN  files in folder engagements
    /write_subblock_engagements(e)
  END DO 
&

FUNCTION:write_subblock_engagements
    WRITE_LINE WRITE_TAG e, `f.period`  from filename
    WRITE_LINE WRITE_TAG e, `e.organization_name` 
    WRITE_LINE WRITE_TAG e, `e.job_title` 
    WRITE_LINE WRITE_TAG e, `e.text_block_work` 
    WRITE_LINE WRITE_TAG e, `e.text_block_achievements` 
    WRITE_LINE WRITE_TAG e, `e.text_block_keywords` 
    WRITE_LINE thin light grey line  
  END DO
&  

content is not in the header but at the bottom in grey
WRITE now() FORMAT "DD MMMM YYYY"