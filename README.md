# hquery
A wxPython GUI for Windows to query the HUGO gene database

### Contact Information

This program was written for NIH BTRIS to retrieve information on genes from
the [HUGO gene database](http://www.genenames.org/) API.

It is maintained by [Steven Lakin](mailto:Steven.Lakin@colostate.edu)

### Getting started

The hquery.py file is provided for testing and debugging purposes.  End users
will want to use the hquery.pyw to suppress the python console.  To start up
the program, ensure that you have the necessary dependencies installed.  You 
will need the following to be installed on your machine:

+ [Python 3.x.x](https://www.python.org/downloads/)
+ [Requests Python package](http://docs.python-requests.org/en/latest/user/install/#install)

Double click on hquery.pyw to open the program.  Select "Open File" from the
"File" menu (File > Open File) and choose a gene batch file from your machine.
Gene batch files should be utf-8 (standard encoding) text files (.txt) that
contain one gene symbol per line:

Example:

```
BRCA1
MAPK
ZNF3
```


The gene symbols should be standard (less than 6 characters or otherewise as
indicated by HGNC).  Improperly formatted gene symbols may return no result.
Null results are recorded in the RejectedQueryReport file that this program
outputs.

The location of your gene batch (input) file will be the same directory to which
this program writes.  The following files will be output after each query:

+ GeneQueryResults_[timestamp].txt
+ RejectedQueryReport_[timestamp].txt

The GeneQueryResults file contains the requested gene information in a format
that can be subsequently fed into the NCI Apellon OntyLog batch uploader. The
RejectedQueryReport contains a list of all gene symbols that returned no results
or returned an error code from the API.  If an error code was returned, its
code will be listed as a standard [REST API status code](http://www.restapitutorial.com/httpstatuscodes.html).

For very large queries (more than 1000 gene symbols), you should first contact
the [HGNC](http://www.genenames.org/about/contact-details) to request permission for a large query.

This program has no built-in wait time between queries, so running very large
queries without contacting HGNC could result in a temporary denial of service
from the server.

For questions or update requests, contact me at the email listed above.