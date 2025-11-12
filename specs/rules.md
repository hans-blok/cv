[R1]
RULE 
data files start with the attirbute `attribute` these must be ignored for WRITE_LINE
EXAMPLE
`year`|`name`|`learning_institute` IN courses.txt must be ignored


[R2]
RULE 
all tags are in Dutch
EXAMPLE
Roepnaam and not Usual name

[R3]
RULE 
block titles are written in capital and bold
EXAMPLE
OPLEIDINGEN

[R4]
RULE 
writing of tags can not be hardcoded, they are found in file functional_dm (tag)
EXAMPLE
PERSONAL
`name` (naam)
`usual_name` (roepnaam)
`place_of_residence` (woonplaats)
`date_of_birth` (geboortedatum)
`available` (beschikbaar)
`job_title` (functie)
`linkedin_url` (linkedin)
`website_url` (website)
`github_url` (github)

WRITE_TAG p p.`name` means that Naam  Jan Jansen is written


[R5]
RULE 
'block_title' is written bold

[R6]
RULE 
tags are written bold

[R6]
RULE 
tags related to attributes start with a capital. 
rest of the tag follows convention: eg. LinkedIn is preferred above Linkedin 



