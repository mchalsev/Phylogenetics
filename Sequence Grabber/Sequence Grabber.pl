#!/usr/bin/perl
#Author: Maria Chalsev
#Date: 30.03.16

#********************************************************************************************************************
                                               #   ..BioPerl Sequence Grabber..  #
#The purpose of this program is to extract specific information from a biological database, namely NCBI GenBank, by using BioPerl.
# program input: gene name and a file name containing accession numbers
# program output: fasta file containing a binomeal species name as well as gene/protein sequences, according to input. 
#***********************************************************************************************************************

use strict;
use warnings;
use Bio::SeqIO;
use Bio::DB::GenBank;
use Cwd 'abs_path';
use File::Basename;


#get user input from command line 
die "please enter a gene name followed by desired file at the end of command line" unless @ARGV==2;
my $file = $ARGV[0];   #eg. small_list
chomp ($file);
my $gene = $ARGV[1];   #eg. COX1
chomp ($gene);


#open fasta format files for writing. Each file will be named according to input gene. 
my $dna_file_o = Bio::SeqIO-> new (-file=> ">dna_Maria_$gene.fa", -format=> 'fasta');
my $prot_file_o = Bio::SeqIO -> new (-file=> ">aa_Maria_$gene.fa", -format=> 'fasta');
#open user input file for reading. 
open(my $fh, '<', $file) or die "Could not open file '$file' for reading";


#create a GenBank database object that will store information taken from GenBank server
my $db_o = Bio::DB::GenBank->new();

my $seq_o;
# loop through accession IDs in the input file to get the following information from the corresponding GenBank record. 
while (my $id = <$fh>) {
    chomp $id;
    
    # get the record information (in form of a BIO::Seq object) from the GenBank server page corresponding to given accession ID. 
    $seq_o = $db_o->get_Seq_by_acc($id);
    
    #get the full binomial species name and modify it so that words are separated by underscores. 
    my $species_o = $seq_o->species();
    my $binomial = $species_o->binomial('FULL');
    $binomial=~s/ /_/g;
    #print "binomial name: $binomial\n";
    
    #get the different features in the GenBank record 
    my @SeqFeatures = $seq_o -> get_SeqFeatures();
    
    my (@genes, @aaSeq, $genes, $feature, $subseq);
    #loop through the different features: 
    foreach $feature (@SeqFeatures) {
        #get the primary tag for each feature 
        my $fptag = $feature -> primary_tag();
        #print "this is each feature's primary tag: $fptag\n";
        
        #look for a primary tag called CDS, which will contain gene information.
        if ($fptag eq "CDS") {
            #extract the gene names within the CDS of this GenBank record (they are the values of the gene tag).  
            @genes = $feature->get_tag_values('gene');
            #print " these are the genes within this ID's CDS: @genes\n";
            
            #see if the input gene is present within this GenBank record's gene list (ie. within the full sequence), if so do the following: 
            if ( $gene ~~ @genes ) {
                #extract the amino acid sequence from within the translation tag of the CDS of this GenBank record.  
                @aaSeq = $feature -> get_tag_values('translation');
                
                #based on the specified location of the gene with the CDS, extract the sequence of the input gene. 
                    #get the start and end positions of the input gene sequence.
                my $start= $feature->start();
                #print "$start\n";
                my $end= $feature->end();
                #print "$end\n";
                    #determine whether the gene is on the positive or negative strand: 
                my $strand= $feature->strand();
                #print "$strand\n";
                    #get subsequence of the sequence object based on the determined start and end positions. 
                $subseq = $seq_o->subseq($start, $end);
                    #if gene is on the negative strand, get the reverse complement of the subsequence.
                if ( $strand == -1 ) {
                    #had to create an object of subseq because revcom() cannot be used on a string (and subseq() returns a string).
                    my $subseq_o = Bio::Seq->new (-seq => "$subseq");
                    #get reverse complement of the subsequence object 
                    my $revsubseq_o = $subseq_o->revcom();
                    #get the (reverse) DNA sequence out using seq() method 
                    $subseq = $revsubseq_o->seq();
                }
            }    
        }
    }
    #create an object for writing to file based on the information obtained above and then write to file.
        #DNA sequence
    my $aa_to_file = Bio::Seq->new ( -id => "$binomial", -seq => "@aaSeq");
    $prot_file_o->write_seq($aa_to_file);
        #amino acid sequence
    my $dna_to_file = Bio::Seq->new ( -id => "$binomial", -seq => "$subseq");
    $dna_file_o->write_seq($dna_to_file);
    
}


#close input file 
close ($fh) or die "could not close input file handle";


#let user know how many files were created, what their name is and where they are located
    #obtaining full file path
my $dna_path=abs_path("dna_Maria_$gene.fa");
my $aa_path=abs_path("aa_Maria_$gene.fa");
    #parsing full path name into file and location 
my $dirname_dna = dirname($dna_path);
my $dirname_aa = dirname($aa_path);
my $basename_dna = basename($dna_path);
my $basename_aa = basename($aa_path);

print <<FILE;
2 files created:
    File name: $basename_dna    File location: $dirname_dna
    File name: $basename_aa     File location: $dirname_aa
FILE
    
    
    
    
