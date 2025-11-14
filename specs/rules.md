
# Formatting and Data Rules
# These rules define the formatting conventions and data handling principles used to generate the CV in HTML format.
# They ensure consistency, maintainability, and accessibility across all generated documents.

[RULE 1]
Data files shall start with a header record that lists all attribute names.
This header record must be ignored when processing the file with WRITE_LINE.
Example:
year | name | learning_institute in courses.txt must be ignored.

[RULE 2]
All tags shall be written in Dutch.
Example:
Use Roepnaam instead of Usual name.

[RULE 3.1]
Block titles shall be written in uppercase, 
Example:
OPLEIDINGEN
Note: the content should be emphasize not the labels.

[RULE 3.2]
Block titles shall be written in colour #b2bec3 (HEX) 

[RULE 3.1]
Block titles shall be written bold

[RULE 4]
The writing of tags shall not be hardcoded. Tags must be retrieved from the file functional_dm (tag).
Example:
PERSONAL

name                (naam)
usual_name          (roepnaam)
place_of_residence  (woonplaats)
date_of_birth       (geboortedatum)
available           (beschikbaar)
job_title           (functie)
linkedin_url        (linkedin)
website_url         (website)
github_url          (github)


WRITE_TAG p p.name results in “Naam Jan Jansen” being written.


[RULE 6.1]
Tags shall be written in colour #b2bec3 (HEX) 

[RULE 6.2]
Tags shall be written in bold.

[RULE 6.2]
Tags shall be written lowercase starting with a capital.


[RULE 7]
Tags derived from attributes shall start with a capital letter, and the remaining characters shall follow standard capitalization conventions.
Example:
Use LinkedIn instead of Linkedin.

[RULE 8]
Line spacing in the blocks shall be set to 1.4.

[RULE 9]
Line spacing between the blocks shall be set to 1.6.

[RULE 9]
The page shall comply with the Web Content Accessibility Guidelines (WCAG).
This ensures that users with visual impairments can enlarge or zoom the content without any loss of information or distortion of layout.
Images shall be positioned close to their related textual content to maintain semantic and visual association.

[RULE 10]
The site must be responsive. Do not use tables.

[RULE 11]
The logo is place above the text (not at the left)

[RULE 12]
content files are found using a relative path (not C:/gitrepo/cv/content)

[RULE 13]
The urls are written in the sidebare at the left

[RULE 14]
None of the content is bold
EXAMPLE the name of the education is not written bold

[RULE 15]
The colour of the tags and block shall have colour code  #636e72 (HEX)

[RULE 15]
The colour of the lines between the blocks shall have colour code  #b2bec3 (HEX)

[RULE 16]
The colour of the lines between the courses shall have colour code  #dfe6e9 (HEX)

[RULE 17]
The whitespace above and below the separator lines between blocks shall be equal.
The separator line (block-sep) shall have equal margin-top and margin-bottom values to ensure symmetric spacing.

[RULE 18]
urls and contact-info have not a tag. Instead icons shall be written.

[RULE 19] Following colour codes shall be used for the icons
LinkedIn: #0A66C2 (LinkedIn blauw)
GitHub: #181717 (GitHub zwart)
Email: #0072C6 (Microsoft Outlook blauw)
Phone: #00b894 (groen)
Website: #74b9ff (lichtblauw)