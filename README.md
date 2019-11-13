# validatearticledata
Python scripts to validate article data using Crossref 
The scripts read from a csv file with titles and DOIs and:
  - search crossref by title and verify if DOI is OK
  - build three files getting article data from crossref using validated DOIs
    - a file with article data
    - a file with author data
    - a file linking authors to articles
