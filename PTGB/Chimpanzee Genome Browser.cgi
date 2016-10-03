#!/usr/bin/perl
#Author:Maria Chalsev
#Date:Apr 14th, 2016
#Course:BIF724
# I declare that the attached assignment is wholly my own work in accordance with
# Seneca Academic Policy. No part of this assignment has been copied manually or
# electronically from any other source (including web sites) or distributed to other students.
# Name:Maria Chalsev
# ID:035231141


use strict;
use warnings;
use lib '/home/john.samuel/src/ensembl/modules';
use Bio::EnsEMBL::Registry;
use CGI qw/:standard/;
use Bio::Graphics;
use Bio::SeqFeature::Generic;
print "Content-type:text/html\n\n";


#connecting to the Ensembl API:
my $registry = 'Bio::EnsEMBL::Registry';
$registry->load_registry_from_db(
    -host => 'ensembldb.ensembl.org',
    -user => 'anonymous'
);

if (param()){
    
    my $user_start=param("start");
    my $user_end=param("end");
    my $chromosome = param("chroms");
    chomp $user_start;
    chomp $user_end;
            

    my $species = "Pan troglodytes";
    #get a slice adaptor object
    my $slice_adaptor = $registry -> get_adaptor ( $species, 'Core', 'Slice' );

    #-----------------------------------------------------------------------------------    
    #Validation:
    #-----------
    #1. checking for missing values
    #if both text values are missing use default values, if only one is missing print error,  otherwise proceed. 
    my $missVal="";
    my @errors=();
    if (($user_end=="") && ($user_start=="")) {
        $user_start=3000000;
        $user_end=3500000;
    }
    elsif (($user_end=="") || ($user_start=="")) {
        $missVal = "Please enter both a start position and an end position value";  
    }
    else {
        #2. start position validation     
        if ($user_start < 1) {
            push ( @errors , "Start position cannot be less than 1" );
        }
    
        #3. end>start validation 
        if ($user_start > $user_end) {
            push ( @errors , "Start position cannot be greater than end position" );
        }
        my $user_size = $user_end - $user_start;
        #4. difference between text values validation 
        if (($user_size < 1e3) || ($user_size > 10e7)) {
            push ( @errors , "difference between start and end positions must be between 1e3 and 10e7" );
        }
        #5. input containing integers only validation 
        if (($user_start =~ /[^0-9]/) || ($user_end =~ /[^0-9]/)) {
            push ( @errors , "entries must contain integer values only");
        }

        #end position validation 
        #use slice adaptor to get a slice object for the entire chromosome 
        my $wholeChrSlice = $slice_adaptor -> fetch_by_region ( 'chromosome' , $chromosome );
        #determining the end of the slice object of the entire chromosome 
        my $wholeChrEndVal = $wholeChrSlice -> end();
        if ($user_end > $wholeChrEndVal) {
            push ( @errors , "End position exceeds chromosome length" );
        }
    }
#    ----------------------------------------------------------------------------------------------
    #printing errors to screen, if there are any:
    if ($missVal) {
        print "<p><font color='#ff0000'>", $missVal, "</font><br></p>";
        print top_html("Chimp Genome Browser");
        print form(); 
    }
    elsif (@errors) {
        print "<p><font color='#ff0000'>", join("<br>", @errors), "</font><br></p>";
        print top_html("Chimp Genome Browser");
        print form();    
    }
#   ----------------------------------------------------------------------------------------
    else {
        # to display user's chosen region (and later use):  
        #using the slice adaptor obtained in line 58 to get another slice object now containing only a portion of the chromosome, based on      user input. 
        my $slice = $slice_adaptor -> fetch_by_region ('chromosome',$chromosome,$user_start,$user_end );       
        #find start position for the slice 
        my $start = $slice -> start();
        #find end position for the slice. 
        my $end = $slice -> end();
        #find the region (in this case chromosome) of the slice 
        my $chroms = $slice -> seq_region_name();
        #print message to user:
        print "Report for region: Chimpanzee (Pan troglodytes) chromosome ", $chroms , " from ", $start , " to ", $end;
#        -----------------------------------
        #To create the chart and graphics        
        #get a reference to an object representing all the genes within the slice
        my $genes_ref = $slice -> get_all_Genes();
        #dereference the reference object to obtain an array containing all the genes in the object. 
        my @genes = @$genes_ref; 
#---------------------------------------------------------------------------------------------------------
#Output chart headings:
        print top_html("chr $chroms:$start-$end");
        print <<CHART_HEAD;
        <table border="1" align = "center" width="80%">
        <tr>
        
            <td align="center">Gene id</td>
            <td align="center">start</td>
            <td align="center">end</td>
            <td align="center">strand</td>
            <td align="center">length</td>
            <td align="center">description</td>
            <td align="center">extrenal name</td>
            <td align="center">gene type</td>
            <td align="center">status</td>
            <td align="center">number of transcripts for that gene</td>
        </tr>
CHART_HEAD
            #graphics
        my $size = $end-$start;
        #create a panel to contain everything 
        my $panel = Bio::Graphics::Panel->new(-length => $size, -width  => 800, -pad_left=>100, -pad_right=>100,
            -start=>$start,-end=> $end);
        #create an object to represent the scale bar
        my $scale = Bio::SeqFeature::Generic->new(-start => $start,-end => $end );
        #add your scale to the panel and configure settings
        $panel->add_track($scale,-glyph => 'arrow',-tick => 2,-fgcolor => 'black',-double  => 1);
    
        #iterate through genes array to get required information         
        if (@genes) {
            
            foreach my $gene (@genes) {
                #get gene id
                my $id = $gene->stable_id();
                #get gene start position 
                my $geneStart = $gene->seq_region_start();
                #get gene end position 
                my $geneEnd = $gene->seq_region_end();
                #get gene strand
                my $geneStrand = $gene->strand();
                #convert gene strand from 1 and -1 to +ve and -ve. 
                if ($geneStrand==1) {
                    $geneStrand = "+";
                }
                else {
                    $geneStrand = "-";
                }
                #get gene length 
                my $geneLength = $gene->length();
                # get gene description 
                my $geneDesc = $gene->description();
                #get gene external name 
                my $geneExtName = $gene->external_name();
                #get gene type: protein coding, etc. 
                my $geneType = $gene->biotype();
                #get status of gene
                my $geneStatus = $gene->status();
                #get an array of all transcripts in gene object
                my @GeneTrans = $gene->get_all_Transcripts();
                #get number of transcripts in gene by iterating through transcripts and counting them 
                my$geneTransNum=0;
                foreach my $transcript (@GeneTrans) {
                    $geneTransNum++;
                }
                
                #graphics for each gene: 
                #create a new track individually for each gene, set color of font for gene id and position depending on whether the gene is protein coding or not. 
                my $color="";
                if ($geneType eq "protein_coding") {
                    $color='red';
                }
                else {
                    $color='black';
                }
                my $track = $panel->add_track(-glyph => 'transcript2', -stranded => 1, -label => 1, -fontcolor => $color, 
                -bgcolor => 'green', -description=>$geneType);
                #create an object for each gene
                my $displayName = "$id ($geneStart-$geneEnd)";
                my $feature = Bio::SeqFeature::Generic->new(-display_name => $displayName, -strand => $geneStrand, -start => $geneStart, -end => $geneEnd);
                #add gene to panel
                $track->add_feature($feature);
        
#        print the chart rows with all the information acquired
                print <<CHART_BODY;
                    <tr>
                        <td align="center"><a href="http://uswest.ensembl.org/Gene/Summary?db=core;g=$id" target="_blank">$id</a></td>
                        <td align="center">$geneStart</td>
                        <td align="center">$geneEnd</td>
                        <td align="center">$geneStrand</td>
                        <td align="center">$geneLength</td>
                        <td align="center">$geneDesc</td>
                        <td align="center">$geneExtName</td>
                        <td align="center">$geneType</td>
                        <td align="center">$geneStatus</td>
                        <td align="center">$geneTransNum</td>
                    </tr>
CHART_BODY
            }
            #close table once all rows have been printed
            print "</table>";
            #open an image file for writing or die. 
            open FH, ">graphics.png" or die $!;
            #print panel object to file 
            print FH $panel->png;
            #close file
            close FH;
            #print image to screen 
            print "<img src='graphics.png'/>";
            #print a link to return to form 
            print qq(<div style="text-align: center"><a href="$0"> New Search </a>);
        }
        else {
            #if no genes were found print no genes found in a row below the table headings. 
            print qq(<tr><td colspan="10" align="center"> no genes found </td></tr>);
            #close table
            print "</table>";
            #print a link to return to form 
            print qq(<div style="text-align: center"><a href="$0"> New Search </a>);
            
        }
    }
}    
  
else{
    print top_html("Chimp Genome Browser");
    print form();
}
print bottom_html();

sub form {
    my $s= param('start');
    my $e= param('end');
    my $chr=param('chroms');
    #create an array for all the options to go in the drop down menu
    my @chr = qw/1 2a 2b 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 X Y MT/;
    my @options;
    #iterate through each item in array and create a drop down option in html out of each one.
    foreach (@chr) {
        my $sel="";
        # option 3 is default, so if $chr is null (ie no user input) the dropdown will select option 3.
        #if $chr isn't null (ie a selection was previously made by the user) the dropdown value will be set to that value. 
        $sel= "selected='selected'" if ((($_ == 3) && ($chr eq "")) || ($chr eq "$_"));
        my $var= qq(<option $sel value="$_" $chr>$_</option>);
        push (@options, $var);
    }
    return<<FORM;        
        <form action ="$0" method = "get">
        Chromosome: <select name="chroms">
        @options
        </select><br><br>
        Start Position: <input type = "text" name="start" value="$s" placeholder = "3000000"><br><br>
        End Position: <input type = "text" name="end" value="$e" placeholder= "3500000" ><br><br>
        <input type = "submit" ></td></tr>
        </form>    
FORM

}
sub top_html {
    my $title=shift @_;     # or $_[0]; 
    return<<TOP;
<!DOCTYPE html>
<html background-color: lightblue>
    <head>
        <title> $title </title>     
    </head>
    <body bgcolor="#FFA500">
        <h1 align="center"> the CHIMP-O-Browser </h1>
        <h3 align="center">(your new favorite chimpanzee genome browser)</h3>
        
        <h4><i>Instructions</i></h4>
        
        <p><i>This browser lets you walk along the chromosomes of the common chimpanzee (Pan troglodytes) based on the Ensembl database<br>
        The common chimpanzee is a species of great ape. It has 26 chromosomes and a mitochondrial genome.
        <br>select a chromosome and position range (start and end) to browse through and view it in tabular and graphical form. <br>
        
        <br><u>Keep in mind the following rules: </u><br>
        
        1. Start position cannot be less than 1 <br>
        2. End position cannot be greater than the end of a chromosome <br>
        3. Start position cannot be greater than end position <br>
        4. Both position fields must be filled out in order to browse<br>
        5. The difference between start and end cannot be less than 1e3 or greater than 10e7
        6. values for start and end positions must be integers only
        
        <br> <b>If you wish to see an example of output simply click submit.</b> <br>
        
        examples with at least 3 genes: <br>ex1. chr 2a: 207000-600000 has genes: SH3YL1, ACP1 and FAM150B.<br>
        ex2: chr 19: 4673820-4806336 has genes: C19ORF10, DPP9, ptr-mir-7-3 and FEM1A. <br>
        ex3: chr 5: 77788866-78669159 has genes:NUP155, U7, C5ORF42, Metazoa_SRP, NIPBL, SLC1A3<br>
        Example with no genes: chr 17:1-1003 has no genes
        </i>
        </p>
TOP
}

sub bottom_html {
    return<<BOTTOM;
    </body>
</html>
BOTTOM
}


