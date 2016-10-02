#!/usr/bin/perl
#Name:Maria Chalsev
#Date: 02 29 16
#declaration:

# Name: Maria Chalsev
# ID: 024231141
#------------------------------------------------------------------------------

#titles and menu subroutine

sub top_html {
    my $title=shift @_;     # or $_[0]; 
    return<<TOP;
<!DOCTYPE html>
<html style="background:#D8CEF6">
    <head>
        <title> $title </title>
    </head>
    <body>
        <h1 align ="center"><font color=#898989 size=6> RE1 target gene data </font></h1>
        <h2 align ="center"><a href="./Maria_a1_add.cgi">Add a record</a>  &nbsp|&nbsp  <a href="./Maria_a1_view.cgi">view all records</a> &nbsp|&nbsp <a href="./Maria_a1_upload.cgi">upload a file</a></h2>

TOP
}

#html closing subroutine

sub bottom_html {
    return<<BOTTOM;
    </body>
</html>
BOTTOM
}

#data validation subroutine

sub validate {
    my $data= shift(@_);
    my @errors;
    #validate that all user inputs meet the format requirements for each field.
        #if a non-null field remains empty after submission, error will prompt user to enter information for that field. 
    if (@{$data}[0] !~ /^((rat|opossum|human|xenopus|chicken)_(42)_([0-9]{1,2}[a-z]{0,1})_(([0-9]{1,2})|([W|X|Y|Z])|(scaffold_[0-9]{1,7}))_([0-9]{1,9})_(f|r))$/) {
        push @errors, "Invalid RE1 ID format. Please check instructions at the top of the page for correct format";
    }
    if (@{$data}[1] !~ /^(([1|0])(\.{1}9{1}[1-9]{1}[0-9]{0,2}){0,1})$/) {
        push @errors, "Invalid RE1 PSSM score format. Please see instructions at the top of the page for correct formatting.";
    }
    if (@{$data}[2] !~ /^(ENS(G|XET|SMO|RNO|GAL)(G)([0-9]{11}))$/) {
        push @errors, "Invalid Target Gene ID format. Please check instructions at the top of the page for correct formatting.";
    }
    if (@{$data}[3] !~ /^(3'|5'|exon|EXON|intron|INTRON)((\+){0,1})$/) {
        push @errors, "Invalid RE1 position format. Please check instructions at the top of the page for correct formatting.";
    }
    # ensures that user filled in the radio button field, if they didn't then program prompts them to do so. 
    unless ((@{$data}[4] eq "+") || (@{$data}[4] eq "-")) {
        push @errors, "Target gene strand was not selected. Please select strand. ";
    }
    if (@{$data}[5] =~ /([\\|\'|\"])/) {
        push @errors, "Description cannot contain backward slash or quotations marks. ";
    }
    unless ((@{$data}[0] =~ /(rat)/) && (@{$data}[2] =~ /(RNO)/) ||
    (@{$data}[0] =~ /(opossum)/) && (@{$data}[2] =~ /(SMO)/) ||
    (@{$data}[0] =~ /(human)/) && (@{$data}[2] =~ /(GG)/) ||
    (@{$data}[0] =~ /xenopus/) && (@{$data}[2] =~ /XET/) ||
    (@{$data}[0] =~ //) && (@{$data}[2] =~ //) ||
    (@{$data}[0] =~ /chicken/) && (@{$data}[2] =~ /GAL/)) {
        push @errors, "RE1 ID and Target gene ID must correspond to the same species!";
    }
    
    return @errors;
    
}

#instructions subroutines: 

sub add_instruct {
    return<<add_instruct
<!DOCTYPE html>
<html>
    <body> <font color=#82E0AA">
        <h4>Please fill out form according to the following instructions:</h4>
        <p> 1. RE1 ID must include species name, ensemble database number (42), version number, region name, position on the region and strand of RE1(f/r), all separated by underscores. 
        <br>2. Score can only be a number between 0.91 and 1, all numbers except 1 can contain decimal digits(up to 4).
        <br>3. RE1 Target gene is a number beginning with ENS followed by the species code, the letter G and an 11 digit long number(no spaces). 
        <br>4. NB:RE1 and Target Gene must both come from the same species!.
        <br>5. RE1 position is the position of your RE1 relative to the target gene. Entry options are case insensitive: 3', 5', exon, intron, exon+, intron+
        <br>6. Description cannot include the following symbols: ', '', / or \\ </p><br>
    </body>
add_instruct
}

sub view_instruct {
    return<<view_instruct
<!DOCTYPE html>
<html>
    <body> <font color=#82E0AA">
        <h4> The following table includes data collected through RE1 research, including your contributed input records: <br> This table is user interactive, you may: </h4>
        <p> 1. sort data alphanumerically by RE1 ID, PSSM score for an RE1, RE1 Target gene ID or RE1 chromosomal position by clicking on the colored/underlined table headings.      
        <br>2. find out more about an RE1 through Ensembl by clicking on each individual RE1 Target gene ID.  
        <br>3. add additional records via web form or uploaded file by clicking on the buttons at the top of the page. 
    </body>
view_instruct
}

sub upload_instruct {
    return<<upload_instruct
<!DOCTYPE html>
<html >
    <body> <font color=#82E0AA">
        <h4> Instructions for file upload: </h4>
        <p> 1. uploaded file must be a .csv file and file name cannot include \" or '. 
        <br>2. all entried within your file must be valid before the file data can be stored in the RE1 database.  
        <br>3. Please ensure record fields meet the following format:
            <br>&nbsp&nbsp a. RE1 Target gene is a number beginning with ENS followed by the species code, the letter G and an 11 digit long number(no spaces). 
            <br>&nbsp&nbsp b. NB:RE1 and Target Gene must both come from the same species!.
            <br>&nbsp&nbsp c. RE1 position is the position of your RE1 relative to the target gene. Entry options are case insensitive: 3', 5', exon, intron, exon+, intron+
            <br>&nbsp&nbsp d. Description cannot include anything other than letters, numbers and the symbols - and _ </p>
        </font>
    </body>
upload_instruct
}

1;
