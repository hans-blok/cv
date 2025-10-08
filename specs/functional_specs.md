# Functional design html-generator


# ( example ) means entity
# ` means data item
# / means initatie function


DO FOR ALL BLOKKEN (blocks.txt)
    WRITE `block_title (formaat vet en in hoofdletters)
    SEARCH FILE met file-naam gelijk aan `blockname
    IF `blockname = personal THEN
       /write_personal
       WRITE grijze_blok_lijn
    IF `blockname = education THEN
       /write_education
       WRITE grijze_blok_lijn
    IF `blockname = courses
       /write_courses
       WRITE grijze_blok_lijn
    IF `blockname = courses_short THEN
       /write_courses_short
       WRITE grijze_blok_lijn
    IF `blockname = engagements THEN
       /write_engagements
       WRITE grijze_blok_lijn
END DO FOR ALL
   

FUNCTION:write_personal
 DO FOR ALL instances in PERSONAL
    WRITE the tag plus the value 
END DO FOR ALL

FUNCTION:write_education
DO FOR ALL instances in EDUCATION
    WRITE a line with `period `name `place
    'addition placed under `name
END DO FOR ALL

FUNCTION:write_course
 DO FOR ALL instances in COURSE
    WRITE a line with `year, `name, and `learning_insitute
END DO FOR ALL

FUNCTION:write_courses_short
 DO FOR THE instances in COURSES_SHORT
    WRITE a line with `period, `text_various_courses
    WRITE a line with `text_block placed under `text_various_courses
    where the text is wrapped and items are ended with a comma except the last one.


FUNCTION:write_engagements
DO FOR ALL files in folder engagements
    /write_subblock_engagements
END DO FOR ALL

FUNCTION:write_subblok_engagements
DO FOR ALL files in folder engagements
    WRITE a line with the tag, `period  
    WRITE a line with the tag, `function
    WRITE a line with the tag, `text_block_work
    WRITE a line with the tag, `text_block_achievements
    WRITE thin light grey line  
END DO FOR ALL