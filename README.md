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

Required packages/software:
- [wxPython for Python 2.7](http://www.wxpython.org/download.php#msw)
- [Python 2.7.x](https://www.python.org/downloads/)
  * [Requests Python package (can be pip installed)](http://docs.python-requests.org/en/latest/user/install/#install)
  * [openpyxl Python package (can be pip installed)](https://openpyxl.readthedocs.org/en/latest/#Installation)
- [R Language for Statistical Computing](https://www.r-project.org/)
  * splitstackshape package for R
  * dplyr package for R
  * stringr package for R
  * openxlsx package for R
  * xlsx package for R
- (Optional) [Cygwin](http://cygwin.com/install.html)

**Note: You must install the same architecture of R as your Java JRE/JDK**
64-bit R must be used with 64-bit JDK/JRE, and 32-bit with 32-bit

**Note: the Rscript executable MUST be added to your Path variable**
This is normally found in:
C:\Program Files\R\R-version#\bin for 64-bit
C:\Program Files (x86)\R\R-version#\bin for 32-bit

#### Step by Step Instructions for Installation

1. Download the [wxPython framework](http://www.wxpython.org/download.php#msw)
2. Download and install the newest version of [Python 2.7.x](https://www.python.org/downloads/)
3. Download and install the newest version of [R Language for Statistical Computing](https://www.r-project.org/)
4. Open the window's command prompt
5. Type the following commands, then close the terminal:
  * C:\Python27\python.exe -m pip install requests
  * C:\Python27\python.exe -m pip install openpyxl
6. From the program file menu, open the R executable
7. Type the following command, then close the R terminal:
  * install.packages(c('splitstackshape', 'dplyr', 'stringr', 'openxlsx', 'xlsx'))
8. (Optional) Download and install Cygwin (for Dani only), be sure to install the "wget" and "unzip" utilities

Double click on hquery.pyw to open the program.  

### Usage and Input Formats

#### Pivoting RED Reports

Menu location:
Gene Query > Pivot Report

1. Select an input file (Must conform to the standards described below)
2. The output file will be named "pivotedReport_[timestamp].xlsx"

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

Menu location:
Gene Query > Load Query List

1. Select an input file (Must conform to the standards described below)
2. Choose a file name for the output file
3. Three files will be output:
  * [YourFileName]_[timestamp].tab
  * ExpandedQueryReport_[timestamp].tab
  * FailedQueryLog.tab

Successful query output will be found in the output file
"[YourFileName]_[timestamp].tab".  If the query returned multiple results
for a single field, those results will be pipe-delimited "|".  The
"ExpandedqueryReport_[timestamp].tab" file contains the same information but
these pipe-delimited values have been split into their own columns.  Empty
fields were converted to NULL.  The "FailedQueryLog_[timestamp].tab" file
contains any query that did not return data or any symbol from the input file
that did not pass the validation filters.  Each error text and symbol is listed
next to its concept name in tab delimited format.

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
this program writes.

This program runs on a single thread and should not cause issues for the queried server.

#### Download and Extract Pharmocologic Index Files

Menu Location:
Pharm Data > Get Pharm Data

1. Select a destination directory (a new one will be created if not present)
2. The files will be downloaded in .zip archived/compressed
3. If you have Cygwin installed, you may choose to extract the data automatically

To download the most recent pharmocologic index files from the NLM ftp server,
click on the "Pharm Data" tab in the menu bar and select "Get Pharm Data".
You will be prompted to select a download directory (folder) for the data
download.  Click OK and wait (this may take several minutes depending on
your connection speed).  

When the download is complete, you will be prompted
to extract the the files using [Cygwin](http://cygwin.com/install.html).  If you do not have Cygwin installed,
you cannot use this option and will have to find a different way to extract
the 2000+ zip files in the downloaded archive.

#### Extract Substance Classes

Menu Location:
Pharm Data > Extract Substance Classes

1. Select the input directory that contains the XML files downloaded previously
2. Enter a file name for the output file
3. The output file will contain any substance data present in the XML files

The pharmocologic index files are a set of XML files containing data for each
known substance in the NLM SPL database.  The hquery GUI contains a script
written to pull the substance name, class, and version from each of these XML
files and output this information into a comma separated file in the
output location of your choice.

In order to utilize this feature, click on the "Pharm Data" tab in the menu bar
and select "Extract Substance Classes".  You will be prompted to select the
folder where the pharmocologic XML files reside and an output directory of your
choice.  The script will then read each XML file, extract the data, and output
the data to a comma separated file.

The output file contains the Substance Name, Substance Class, and Version #.

#### Get Differentials Between Substance Files

Menu Location:
Pharm Data > Pharm Diff

1. Select two files by Ctrl + clicking them
2. A new file will be output called "pharmDiffResults_[timestamp].csv"

In order to compare (or "diff") two files in the same format, click on the
"Pharm Data" tab in the menu bar and select "Pharm Diff".  You will be prompted
to select the files you want to compare.  You will need to select two files
from this menu, which you can do by *clicking first on file number 1, then
Ctrl + click on file number 2.*  Select OK and you will then be prompted to
type the name of the desired output file.  Click OK and the files will be "diffed"
and any entries that are different between the files will be output to the file
whose name you specified in the same directory as the compared files.

This differential determination works by hashing each row in each file and
searching the other file for the same hash.  It will work on any two files, and
if anything is different between the two (including encoding or white space),
it will detect the difference and output the results.

#### Questions?

For questions or update requests, please contact me at the email listed above.

This documentation was last updated on July 24th, 2015