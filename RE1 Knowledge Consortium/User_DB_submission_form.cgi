#!/usr/bin/perl
#Name:Maria Chalsev

#Date: 02 29 16
#declaration:

# Name: Maria Chalsev
# ID: 024231141
#------------------------------------------------------------------------------
use strict;
use warnings;
use CGI qw/:standard/;
require '../Assignment1/Maria_a1_lib.pl';
use DBI;
require '/home/bif724_161a05/.secret';
#if param not empty then process the form
if (param()){
    #each user entry is stored in a variable
    my $re1_id=param("re1 id");
    my $score=param("score");
    my $target_gene_id=param("target gene id");
    my $re1_pos=param("re1 position");
    my $which_strand=param("strand");
    my $description=param("gene description");
    #create an array of user entries for easy feeding into validation subroutine 
    my @entries = ("$re1_id", "$score", "$target_gene_id", "$re1_pos", "$which_strand",  "$description");
    # run validation subroutine (on a reference to entries) and store the return values into an array.
    my @return=validate(\@entries);
    #if no validation errors, proceed with program
    unless (@return) {
        # to avoid the content-type display issue, I created a subroutine that's called below content type. 
        #print "Content-type:text/html\n\n";
        my $password=get_paswd();
        my $dbh=DBI->connect ("DBI:mysql:host=db-mysql;database=bif724_161a05","bif724_161a05", $password) or die "could not connect to DB" . DBI-> errstr;  #last part is actual error from the db
        my $sql = "insert into a1_data values (?,?,?,?,?,?)"; 
        my $sth = $dbh->prepare($sql) or die "could not prepare query" . DBI->errstr;
        my $rowsInserted = $sth-> execute($re1_id, $score, $target_gene_id, $re1_pos, $which_strand,  $description) or die "could not execute query" . DBI->errstr;   
        $dbh->disconnect() or die "problem with disconnect" . DBI->errstr;
        #ensuring that rows were in fact inserted, printing view page if they did.
        if ($rowsInserted==1) {
            print "Location:Maria_a1_view.cgi\n\n";
        }
    }    
    # if validation errors found - print the errors. 
    else {
        print "Content-type:text/html\n\n";
        #print titles and menu
        print top_html("RE1 Submission Form");
        #print instructions
        print add_instruct();
        print "<u><b>The following errors occured:</u></b></br></br>";     
        #print errors
        foreach (@return) {
            print "<font color=#FF0000>$_</font></br><br>";
        }
        print "<br>";
        #print form again
        print form();          
    }
}    
      
else {
    #form not submitted, so display form again
    print "Content-type:text/html\n\n";
    print top_html("RE1 Submission Form");
    print add_instruct();
    print form();          
}

print bottom_html();

sub form {
    my $i= param('re1 id');
    my $sc= param('score');
    my $t= param('target gene id');
    my $p= param('re1 position');
    my $strand= param('strand');
    my $gd= param('gene description');
    my $positive=$strand eq '+'?"checked":"";
    my $negative=$strand eq '-'?"checked":"";
    
    
    return<<form;
    <form action="$0" method="post">
    <table align="center" frame="box" width="30%" cellpadding="4" cellspacing="5">
    <tr><td><b><font size="4"> RE1 ID: </font></b></td></tr>
    <tr><td align="center"><input type="text" name="re1 id" placeholder="eg. rat_42_33_2_41879955_f" value="$i" style="width:450px;"></td></tr>
    <tr><td><b><font size="4">RE1 PSSM Score: </font></b></td></tr>
    <tr><td align="center" ><input type="text" name="score" placeholder="eg. 0.9778" value="$sc" style="width:450px;"></td></tr>
    <tr><td><b><font size="4">Target Gene ID:  </font></b></td><tr>
    <tr><td align="center"><input type="text" name="target gene id" placeholder="eg. ENSGALG58574620983" value="$t" style="width:450px;"></td></tr>
    <tr><td><b><font size="4">RE1 Position: </font></b></td></tr>
    <tr><td align="center"><input type="text" name="re1 position" placeholder="eg. EXON+" value="$p" style="width:450px;"></td></tr>
    <tr><td><b><font size="4">Strand of target gene: </font></b></td></tr>
    <td align="center"> positive: <input type="radio" name="strand" value="+" $positive> negative: <input type="radio" name="strand" value="-" $negative></td></tr>
    <tr><td><b><font size="4">Gene Description: </font></b></td></tr>
    <tr><td align="center"><textarea name="gene description" placeholder="Please describe your gene" rows="5" cols="70">$gd</textarea></td></tr>    
    <tr><td align="center"><input type="submit" style="height:30px; width:90px"> <align=right"> <input type="reset" style="height:30px; width:90px"></td></tr>
        
    </table>
    </form>
form
}
