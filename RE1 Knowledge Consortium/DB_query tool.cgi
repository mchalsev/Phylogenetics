#!/usr/bin/perl
#Name:Maria Chalsev
#Student ID: 035231141
#course:bif724
#instructor: John Samuel
#Date: 02 29 16
#declaration:
# I declare that the attached assignment is wholly my own work in accordance with
# Seneca Academic Policy. No part of this assignment has been copied manually or
# electronically from any other source (including web sites) or distributed to other students.
# Name: Maria Chalsev
# ID: 024231141
#------------------------------------------------------------------------------

use strict;
use warnings;
use CGI qw/:standard/;
require '../Assignment1/Maria_a1_lib.pl';
use DBI;
require '/home/bif724_161a05/.secret';
print "Content-type:text/html\n\n";

# sorting values in a column selected by the user.
#User selection goes into special hash, based on that the program decides which query will be used on the database.   
my $var="select * from a1_data";
if ($ENV{'QUERY_STRING'} eq "sort=re1") {
    $var="select * from a1_data order by re1_id asc";
}
if ($ENV{'QUERY_STRING'} eq "sort=score") {
    $var="select * from a1_data order by score asc";
}
if ($ENV{'QUERY_STRING'} eq "sort=target") {
    $var="select * from a1_data order by gene_id asc";
}
if ($ENV{'QUERY_STRING'} eq "sort=pos") {
    $var="select * from a1_data order by re1_rel_pos asc";
}
#connect to database pass a query to it and have the query executed. 
my $password=get_paswd();
my $dbh=DBI->connect ("DBI:mysql:host=db-mysql;database=bif724_161a05","bif724_161a05", $password) or die "could not connect to DB" . DBI-> errstr;  #last part is actual error from the db
my $sql = $var;  #query varies according to user selection. 
my $sth = $dbh->prepare($sql) or die "could not prepare query" . DBI->errstr;
my $rows_fetched = $sth-> execute() or die "could not execute query" . DBI->errstr;
#print titles and menu
print top_html("a1_data");
#print instructions
print view_instruct();
#print table headings including, some with sorting functionality.
print <<TableHead;
    <br><table style="font-size:17px" align="center" border="1" cellpadding="4" cellspacing="4" width="95%">
        <tr><th><font size=4><a href="./Maria_a1_view.cgi?sort=re1">RE1 ID</a></font></th>
        <th><font size=4><a href="./Maria_a1_view.cgi?sort=score">RE1 PSSM Score</a> </font></th>
        <th><font size=4><a href="./Maria_a1_view.cgi?sort=target">RE1 Target <br>Gene ID</a> </font></th>
        <th><font size=4><a href="./Maria_a1_view.cgi?sort=pos">RE1 Relative Position</a></font></th>
        <th><font size=4> Strand of RE1</font></th>
        <th><font size=4> Gene Description</strong></font></th></tr>
TableHead


my @row;
#if rows were returned, place one row after another in an html table. 
if ($rows_fetched != 0) { 
    while (@row = $sth -> fetchrow_array) {   
        print "<tr><td>$row[0]</td><td>$row[1]</td><td><a add target='_blank' href=http://uswest.ensembl.org/Gene/Summary?db=core;g=$row[2]>$row[2]</a></td><td>$row[3]</td><td>$row[4]</td><td>$row[5]</td></tr>";
    }
}
else {
    print "<tr><td> Error: no queries returned </td><tr>";  
}
#disconnect from database. 
$dbh->disconnect() or die "could not disonnect from DB" . DBI->errstr;