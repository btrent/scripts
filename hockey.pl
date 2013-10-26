#!/usr/bin/perl

`mv hockey.key hockey.key.old`;
`mv hockey.m3u8 hockey.m3u8.old`;

my $team = "flyers";
#$team = "sharks";

my $ipadUrl = $team . "_hd_ipad";

my $m3u8 = `curl -s "http://208.92.36.37/nlds/as3/get_games.php?client=nhl&playerclient=hop" | grep $ipadUrl | sed -e 's/^.*>http/http/' | sed -e 's/live.*\$/live/'`;

chomp($m3u8);

$m3u8 .= "/";
$baseUrl = $m3u8;
$m3u8 .= "$team" . "_hd_1600.m3u8";

$keyUrl = `curl -s $m3u8 | grep AES-128 | sed -e 's/^.*URI=//'`;


`wget -U "AppleCoreMedia/1.0.0.8C148 (iPad; U; CPU OS 4_2_1 like Mac OS X; en_us)" -O hockey.key $keyUrl`;

while (true) {
	`wget $m3u8`;

	my $hdUrl = $team . "_hd_1600.m3u8";

	open (A, $hdUrl);
	open (B, '>tmp.m3u8');
	while(<A>) {
		print $_;
		chomp($_);
		if ($_ =~ /AES-128/) {
			print B '#EXT-X-KEY:METHOD=AES-128,URI="http://upvoter.com/hockey.key"' . "\n";
		} elsif ($_ =~ /ts$/) {
			print B $baseUrl . $_ . "\n";
		} else {
			print B $_ . "\n";
		}
	}
	close(A);
	close(B);

	`rm $hdUrl`;
	`mv tmp.m3u8 hockey.m3u8`;

	sleep 20;
}

##EXTM3U
##EXT-X-TARGETDURATION:10
##EXT-X-MEDIA-SEQUENCE:1203
##EXT-X-KEY:METHOD=AES-128,URI="http://upvoter.com/20131017200000.m3u8.key"
##EXTINF:10,
#http://nlds135.cdnak.neulion.com/nlds/nhl/flyers/as/live/flyers_hd_1600_20131018011130.ts
##EXTINF:10,
#http://nlds135.cdnak.neulion.com/nlds/nhl/flyers/as/live/flyers_hd_1600_20131018011140.ts
##EXTINF:10,
#http://nlds135.cdnak.neulion.com/nlds/nhl/flyers/as/live/flyers_hd_1600_20131018011150.ts
##EXTINF:10,
#http://nlds135.cdnak.neulion.com/nlds/nhl/flyers/as/live/flyers_hd_1600_20131018011200.ts
##EXTINF:10,
#http://nlds135.cdnak.neulion.com/nlds/nhl/flyers/as/live/flyers_hd_1600_20131018011210.ts
##EXTINF:10,
#http://nlds135.cdnak.neulion.com/nlds/nhl/flyers/as/live/flyers_hd_1600_20131018011220.ts



