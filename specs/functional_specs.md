# Functional design html-generator


# ( example ) means entity
# ` means data item
# / means initiate (or call) function
# & means END FUNCTION

SEARCH_FILE logo-header.jpg | logo-header.png
WRITE "logo" 
WRITE now() FORMAT "DD MMMM YYYY HH:mm:ss"

DO FOR EACH b IN BLOCKS 
    WRITE_LINE b.title (note: if empty no title is written )
    SEARCH_FILE filename=b.`name
    IF b.`name` = "personal" THEN
       /write_personal
       WRITE_LINE "grijze_blok_lijn"
    IF b.`name` = "certifications" THEN
       /write_certifications
       WRITE_LINE "grijze_blok_lijn"
    IF `b.`name` = "education" THEN
       /write_education
       WRITE_LINE"grijze_blok_lijn"
    IF b.`name` = "courses"
       /write_courses
       WRITE_LINE"grijze_blok_lijn"
    IF b.`name` = "courses_short" THEN
       /write_courses_short
       WRITE_LINE"grijze_blok_lijn"
    IF b.`name` = "engagements" THEN
       /write_engagements
       WRITE_LINE"grijze_blok_lijn"
   END IF
END DO FOR EACH &
   
FUNCTION:write_personal
   DO FOR EACH p IN PERSONAL
    WRITE_TAG p p.`name`
    WRITE_TAG p p.`usual_name`
    WRITE_TAG p p.`place_of_residence`
    WRITE_TAG p p.`date_of_birth`
    WRITE_TAG p p.`job_title`
    WRITE_TAG p p.`linkedin_url`
    WRITE_TAG p p.`website_url`
    WRITE_TAG p p.`github_url`
END DO FOR EACH 
SEARCH_FILE profile-photo.jpg OR profile-photo.png
WRITE_RIGHT "profile-photo.jpg" | "profile-photo.png"
&

FUNCTION:write_education
  DO FOR EACH e IN instances in EDUCATION
    WRITE_LINE `e.period`, `e.name`,`e.place`
    WRITE_LINE `e.addition` outlined with `e.name`
END DO
&

FUNCTION:write_certifications
  DO FOR EACH c IN  instances in CERTIFCATION
    WRITE_LINE `period`, `name`,`place`
    'addition placed under `name`
END DO
&


FUNCTION:write_courses
  DO FOR EACH c IN COURSE
    WRITE_LINE c.`year`, c.`name`, c.`learning_institute`
  END DO
&

FUNCTION:write_courses_short
  DO FOR THE instances in COURSES_SHORT
    WRITE_LINE `period`, `text_block_various_courses`
    WRITE_LINE `text_block placed` under `text_block_various_courses`
    where the text is wrapped and items are ended with a comma except the last one. 
&

FUNCTION:write_engagements
  DO FOR EACH f IN  files in folder engagements
    /write_subblock_engagements(e)
  END DO 
&

FUNCTION:write_subblock_engagements
    WRITE_LINE WRITE_TAG e, `f.period`  from filename
    WRITE_LINE WRITE_TAG e, `e.job_title` 
    WRITE_LINE WRITE_TAG e, `e.text_block_work` 
    WRITE_LINE WRITE_TAG e, `e.text_block_achievements` 
    WRITE_LINE WRITE_TAG e, `e.text_block_keywords` 
    WRITE_LINE thin light grey line  
  END DO
&  