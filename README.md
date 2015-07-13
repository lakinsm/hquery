# hquery
A wxPython GUI for Windows with interfaces to the HGNC REST web-service and
the NLM Pharmocologic SPL Index files on the NLM ftp server.

### Contact Information

This program was written for NIH BTRIS to retrieve information on genes from
the [HGNC gene database](http://www.genenames.org/) API.

It is maintained by [Steven Lakin](mailto:Steven.Lakin@colostate.edu)

### Installation and Getting started

The hquery.py file is provided for testing and debugging purposes.  End users
will want to use the hquery.pyw to suppress the python console.  To start up
the program, ensure that you have the necessary dependencies installed.  You 
will need the following to be installed on your machine:

+ [Python 3.x.x](https://www.python.org/downloads/)
++* [Requests Python package](http://docs.python-requests.org/en/latest/user/install/#install)
++* [openpyxl Python package](https://openpyxl.readthedocs.org/en/latest/#Installation)
+ [R Language for Statistical Computing (pivot feature only)](http://cran.r-project.org/mirrors.html)
+ The R packages (pivot feature only [Lyuba will need this for the pivot]):
++* xlsx
++* dplyr
++* tidyr
++* openxlsx
+ (Optional) [Cygwin](http://cygwin.com/install.html)

Which can be obtained using the following line of code in the R terminal:

install.packages(c('xlsx', 'dplyr', 'tidyr', 'openxlsx'))

Double click on hquery.pyw to open the program.  

### Usage and Input Formats

#### Pivoting RED Reports

To pivot a RED report, the unpivoted input file must be formatted in the
following way.  It should be an *Excel file (.xlsx extension)* containing
exactly the following columns in the following order, which you can see in the
example file "ExampleUnpivotedInputFile.xlsx" provided above:

+ Concept_Name [Column A]
+ Concept_Code [Column B]
+ Gene_Nomenclature_Symbol [Column C]
+ Gene_Chromosome_Location [Column D]
+ Gene_Map_Location [Column E]
+ Full_Synonym [Column F]

The file will be processed in R, which may take some time (up to 5 minutes
for very large reports (> 200,000 rows)).  The file will be pivoted first by
the "Gene_Chromosome_Location" field and then by the "Full_Synonym" field.  The
output file will also be an Excel file (.xlsx extension) output to the same
directory as the specified input report.

#### Gene Query Operations

To load a gene query file, select the "Gene Query" from the menu bar and click
on "Load Query List".  You will be prompted to select a file for the query.
*The format of this file is absolutely strict.*  The file should be formatted
as an *Excel file (.xlsx extension)* exactly as detailed in the
"ExampleGeneQueryFormat.xlsx" file provided above.  It should have the following
columns in exactly this order:

+ Concept_Name [Column A]
+ Concept_Code [Column B]
+ Gene_Nomenclature_Symbol [Column C]
+ Gene_Chromosome_Location#1 [Column D]
+ Gene_Chromosome_Location#2 [Column E]
+ Gene_Map_Location [Column F]
+ Full_Synonym#1 [Column G]
+ Full_Synonym#2 [Column H]
....
+ Full_Synonym#NNN [Column NNN]

The number of "Full_Synonym" columns can be infinite, so long as they are in the
order specified.  There can be *no more than two Gene_Chromosome_Location
columns.*  If there are more than two in the RED report, delete the extra columns
before loading the query file.  Ensure that the query file is not open in any
programs before proceeding with the query.

The gene symbols should be standard (typically less than 6 characters or otherwise as
indicated by HGNC).  Improperly formatted gene symbols may return no result.
Null results are recorded in the FailedQueryLog file that this program
outputs.

The location of your gene batch (input) file will be the same directory to which
this program writes.  The following files will be output after each query:

+ GeneQueryResults_[timestamp].tab
+ FailedQueryLog_[timestamp].txt

The GeneQueryResults file contains the requested gene information in a format
that can be subsequently fed into the NCI Apellon OntyLog batch uploader. The
RejectedQueryReport contains a list of all gene symbols that returned no results
or returned an error code from the API.  If an error code was returned, its
code will be listed as a standard [REST API status code](http://www.restapitutorial.com/httpstatuscodes.html).

This program runs on a single thread and should not cause issues for the queried server.

#### Download and Extract Pharmocologic Index Files

To download the most recent pharmocologic index files from the NLM ftp server,
click on the "Pharm Data" tab in the menu bar and select "Get Pharm Data".
You will be prompted to select a download directory (folder) for the data
download.  Click OK and wait (this may take several minutes depending on
your connection speed).  

When the download is complete, you will be prompted
to extract the the files using [Cygwin].  If you do not have Cygwin installed,
you cannot use this option and will have to find a different way to extract
the 2000+ zip files in the downloaded archive.

#### Extract Substance Classes

The pharmocologic index files are a set of XML files containing data for each
known substance in the NLM SPL database.  The hquery GUI contains a script
written to pull the substance name, class, and version from each of these XML
files and output this information into a comma separated file in the
output location of your choice.

In order to utilize this feature, click on the "Pharm Data" tab in the menu bar
and select "Extract Substance Classes".  You will be prompted to select the
folder where the pharmocologic XML files reside and an output directory of your
choice.  The script will then read each XML file, extract the data, and output
the data to a comma separated file:

+ SubstancePharmAssociations_[timestamp].csv

#### Get Differentials Between Substance Files

In order to compare (or "diff) two files in the same format, click on the
"Pharm Data" tab in the menu bar and select "Pharm Diff".  You will be prompted
to select the files you want to compare.  You will need to select two files
from this menu, which you can do by *clicking first on file number 1, then
Ctrl + click on file number 2.*  Select OK and you will then be prompted to
type the name of the desired output file.  Click OK and the files will be "diffed"
and any entries that are different between the files will be output to the file
whose name you specified in the same directory as the compared files.

#### Questions?

For questions or update requests, please contact me at the email listed above.

This documentation was last updated on July 13th, 2015