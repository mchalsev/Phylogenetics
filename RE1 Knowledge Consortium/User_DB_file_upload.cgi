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
use DBI;
require '../Assignment1/Maria_a1_lib.pl';
require '/home/bif724_161a05/.secret';


my $errorCount=0;
#if any data entered, process form. 
if (param()) {
    my $uploadfile = param('uploaded_file');
    #file name validation
        #if file name contains at least one of the following, bring up an error: a dot other than the extension name dot, a symbol other than alphanumerical _ - . or space.
    if (($uploadfile =~ /([^a-z0-9\.\-\_\s]){1,}/i) || ($uploadfile =~/(\.){2,}/)) {
        print "Content-type: text/html\n\n";
        print "<font color=#FF0000 size=4> error: file must contain no other characters than letters, numbers, - and _</font></br>";    
        $errorCount=1
    }
        #if filename does not contains a .csv extension, bring up an error
    if ($uploadfile !~ /(\.csv)/) {
        if ($errorCount==0) {
            print "Content-type: text/html\n\n";
        }
        print "<font color=#FF0000>error: file must be a .csv file</font>";    

        $errorCount=1;
    }
    #once errors have been printed out at the top of the page, print the upload form again. 
    if ($errorCount==1) {
        print top_html("RE1 Upload Form");
        print upload_instruct();
        print form();
        print bottom_html();
    }
    
    
    #else if no errors in file name, upload the file line-wise into database. 
    else {
        my ($line, $line_good, @error_array, @good_array, @field, @field_good, $error_switch);
        my $upfh=upload('uploaded_file') or die "could not upload file";
        my @lines = <$upfh>;
        #validate each piece of information within each line via subroutine
        foreach $line (@lines) {
            @field=split (',', $line);
            my @return=validate(\@field);
            #if errors found - send to a "bad" array.
            if (@return) {
                push @error_array, $line;
                $error_switch=1;
            }
            #if errors not found-send to a "good" array.
            else {
               push @good_array, $line;
            }
        }
        #if errors occured, print errors to screen. Then print form again. 
        if ($error_switch==1) {
            print "Content-type: text/html\n\n";
            print top_html("RE1 Upload Form");
            print upload_instruct();
            print "<font color=#FF0000 size=5> The following records could not be added to database due to errors in the entry format. <br> please fix errors and try again: </font></br><br>";    
            foreach (@error_array) {
                print "<font color=#DF0101> $_</font><br><br>";
            }
            print form();
            print bottom_html();
        }    
        #if no errors during validation, proceed to uploading data to database.
        #if rows successfully inserted, redirect user to the view page.
        
        #Hi John, I know I have one bug in the next block of code, I struggled for several days to get the content type in the right place so that DB errors get printed to the screen(in case of duplicate entry)
        #AND that location is not interpreted as text but to no avail...content-type placement was by far my biggest challenge during the assignment.
        #I left the content-type line in there that would show DBI errors.
        #(otherwise the assignment was very enjoyable, interesting and not too difficult(only took some time to figure out the logic which was great practice))
        
        #if no errors occured, connect and upload to database. 
        if ($error_switch!=1) {
            #print "Content-type: text/html\n\n";
            foreach $line_good (@good_array) {
                @field_good=split (',',$line_good);
                my $password=get_paswd();
                my $dbh=DBI->connect ("DBI:mysql:host=db-mysql;database=bif724_161a05","bif724_161a05", $password) or die "could not connect to DB\n" . DBI-> errstr;  #last part is actual error from the db
                my $sql = "insert into a1_data values (?,?,?,?,?,?)"; 
                my $sth = $dbh->prepare($sql) or die "could not prepare query\n" . DBI->errstr;
                my $rowsInserted = $sth-> execute ($field_good[0],$field_good[1],$field_good[2],$field_good[3],$field_good[4],$field_good[5]) or die "could not execute query\n" . DBI->errstr;   
                $dbh->disconnect() or die "problem with disconnect\n" . DBI->errstr;
                #if data insertion into database succeeded, redirect user to view page. 
                if ($rowsInserted != 0) {
                    print "Location:Maria_a1_view.cgi\n\n";   
                }
            }        
        }
    }    
}
#display form 
else {
    print "Content-type: text/html\n\n";
    print top_html("RE1 Upload Form");
    print "<h1 align=center>Welcome to the RE1 File upload system</h1><br>";
    print upload_instruct();
    print form();
    print bottom_html();
}

sub form {
    return <<FORM;
    <form action="$0" method="post" enctype="multipart/form-data" align="center">       

        <br><br><h2>Please upload your data file:</h2><br><br>
        <input type="file" name="uploaded_file" style="width:250px;font-size:120%;" ><br><br><br><br>
        <input type="submit" style="width:100px;height:40px;font-size:120%">
    </form>
FORM
}

