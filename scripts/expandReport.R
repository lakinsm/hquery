## expandReport.R

expandReport <- function(infile, outfile) {
    library(splitstackshape)
    
    coldrops <- c()
    
    report <- read.table(infile, 
                         sep='\t', strip.white = T,
                         encoding = "UTF-8",
                         na.strings="",
                         fill=T,
                         header=T,
                         comment.char="",
                         quote="",
                         check.names=F)
    report <- report[,names(report) != ""]
    
    report <- cSplit(report, splitCols=c("Gene_Symbol_Synonyms_HGNC","Gene_Prev_Symbol_Synonyms_HGNC",
                              "Gene_Name_Synonyms_HGNC","Gene_Family_IDs_HGNC","Gene_Family_Names_HGNC",
                              "Enzyme_ID_HGNC","Pubmed_IDs_HGNC"), sep="|")
    
    report <- as.data.frame(report)
    
    for(i in 1:length(names(report))) {
        if(!sum(!is.na(report[, i]))) {
            coldrops <- c(coldrops, names(report)[i])
        }
    }
    
    report <- report[, !names(report) %in% coldrops]
    
    write.table(report, file=outfile, quote=FALSE, sep="\t", na="NULL", row.names=FALSE, fileEncoding="UTF-8")
}

args <- commandArgs(trailingOnly=TRUE)

expandReport(args[1], args[2])