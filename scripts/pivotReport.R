pivotReport <- function(inputReport, outputReport){
    library(xlsx)
    library(dplyr)
    library(tidyr)
    library(openxlsx)
    
    df <- read.xlsx(inputReport, sheet = 2)

    pivot1 <- df %>% 
        group_by(Concept_Name, Concept_Code, Gene_Nomenclature_Symbol, Gene_Map_Location, Full_Synonym) %>%
        mutate(n=paste("Gene_Chromosome_Location#",row_number(), sep="")) %>%
        spread(n, Gene_Chromosome_Location)

    pivot2 <- pivot1 %>% 
        group_by(Concept_Name, Concept_Code, Gene_Nomenclature_Symbol, Gene_Map_Location, `Gene_Chromosome_Location#1`, `Gene_Chromosome_Location#2`) %>%
        mutate(n=paste("Full_Synonym#",row_number(), sep="")) %>%
        spread(n, Full_Synonym)
    
    pivot2 <- as.data.frame(pivot2[,c(1,2,3,5,6,7,8,4,9,18,19,20,21,22,23,24,25,10,11,12,13,14,15,16,17)])
    
    
    xlsx::write.xlsx(pivot2, outputReport, row.names=FALSE, showNA=FALSE)
    
}
