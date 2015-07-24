## For long to wide transformation

args <- commandArgs(TRUE)
        
        
library(dplyr)
library(tidyr)
library(stringr)
library(openxlsx)
library(xlsx)
    
df <- openxlsx::read.xlsx(args[1], sheet = 1)

pivot1 <- df %>% 
    group_by(Concept_Name, Concept_Code, Gene_Nomenclature_Symbol, Gene_Map_Location, Full_Synonym) %>%
    mutate(n=paste("Gene_Chromosome_Location#",str_pad(row_number(), 2, pad="0"), sep="")) %>%
    spread(n, Gene_Chromosome_Location)
    
pivot2 <- pivot1 %>% 
    group_by(Concept_Name, Concept_Code, Gene_Nomenclature_Symbol, Gene_Map_Location) %>%
    mutate(n=paste("Full_Synonym#",str_pad(row_number(), 2, pad="0"), sep="")) %>%
    spread(n, Full_Synonym)
   
locations <- names(pivot2)[grepl('Chromosome_Location', names(pivot2))]
   
synonyms <- names(pivot2)[grepl('Synonym', names(pivot2))]

colOrder <- c('Concept_Name', 'Concept_Code', 'Gene_Nomenclature_Symbol', locations, 'Gene_Map_Location', synonyms)

pivot2 <- as.data.frame(pivot2[,colOrder])

xlsx::write.xlsx(pivot2, args[2], row.names=FALSE, showNA=FALSE)

