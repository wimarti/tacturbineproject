<!doctype html>
<html lang="en">

<?php
$serverIP = "128.153.21.86";
$username = "phpquery";
$password = "dashboard2019";
$dbname = "blackboard_gui";

$conn = new mysqli($serverIP, $username, $password, $dbname);
$query1 = "SELECT MAX(time) FROM blackboard_gui.inverterWeatherData";
$recentTimeReturn = $conn->query($query1);
$recentTime = mysqli_fetch_row($recentTimeReturn)[0];

$query2 = "SELECT * FROM blackboard_gui.inverterWeatherData WHERE time = '" .$recentTime. "'";
$grabData = $conn->query($query2);
$dataToDisplay = mysqli_fetch_assoc($grabData);

$dateObject = date_create_from_format('Y-m-d H:i:s',$dataToDisplay['time']);
$dateToDisplay = date_format($dateObject, "j F, Y g:i a");
$tempC = round($dataToDisplay['TempC']*(9/5)+32);
$windSpeed = round(intval($dataToDisplay['windSpeedMS']*2.2369363,4));
$windHeading = round($dataToDisplay['WindDir']);
$humidity = $dataToDisplay['Humidity'];
$dewpoint = round($dataToDisplay['DewpointC']*(9/5)+32);
$pressure = round($dataToDisplay['PressureMB']);

$power = round(($dataToDisplay['PDC1'] + $dataToDisplay['PDC2'])/2);
$energy = intval($dataToDisplay['ENERGY']);
$minutesToday = intval($recentTime[11].$recentTime[12])*60+intval($recentTime[14].$recentTime[15]);
$avePower = intval($dataToDisplay['ENERGY'])/$minutesToday;
$energyPercentExpected = round($avePower/20.92846*100,2);
$energyPercent = round(100*$energy/30136.9863,2);


$conn->close();
header("Refresh: 60;url='index.php'");
?>

<head>
	<meta charset="utf-8" />
	<link rel="icon" type="image/png" href="assets/img/favicon.ico">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
	
	<title>Clarkson Windmill</title>

	<meta content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0' name='viewport' />
    <meta name="viewport" content="width=device-width" />


    <!-- Bootstrap core CSS     -->
    <link href="assets/css/bootstrap.min.css" rel="stylesheet" />

    <!-- Animation library for notifications   -->
    <link href="assets/css/animate.min.css" rel="stylesheet"/>

    <!--  Light Bootstrap Table core CSS    -->
    <link href="assets/css/light-bootstrap-dashboard.css?v=1.4.0" rel="stylesheet"/>


    <!--  CSS for Demo Purpose, don't include it in your project     -->
    <!--<link href="assets/css/demo.css" rel="stylesheet" />-->


    <!--     Fonts and icons     -->
    <link href="http://maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css" rel="stylesheet">
    <link href='http://fonts.googleapis.com/css?family=Roboto:400,700,300' rel='stylesheet' type='text/css'>
    <link href="assets/css/pe-icon-7-stroke.css" rel="stylesheet" />

</head>
<body>

<div class="wrapper" style="overflow: hidden">
    <div class="sidebar" data-color="green" data-image="assets/img/sidebar-5.jpg">

    <!--

        Tip 1: you can change the color of the sidebar using: data-color="blue | azure | green | orange | red | purple"
        Tip 2: you can also add an image using data-image tag

    -->

    	<div class="sidebar-wrapper">
            <div class="logo">
				<img src="assets/images/clarkson-logo-stacked.png" height="128px" width = "200px" style="margin-left: 10px">
                <a class="simple-text">
                    Clarkson University Ducted Wind Turbine
                </a>
				
            </div>

            <ul class="nav">
                <li class="active">
                    <a href="index.html">
                        <i class="pe-7s-graph"></i>
                        <p>Home</p>
                    </a>
                </li>
                <li>
                    <a href="historical-data.html">
                        <i class="pe-7s-note2"></i>
                        <p>Historical Data</p>
                    </a>
                </li>
                <li>
                    <a href="system.html">
                        <i class="pe-7s-note2"></i>
                        <p>System</p>
                    </a>
                </li>
				
                <li>
                    <a href="learn-more.html">
                        <i class="pe-7s-news-paper"></i>
                        <p>Learn More</p>
                    </a>
                </li>
            </ul>
    	</div>
		<div class="sidebar-background" style="background-image:url(assets/img/sidebar-5.jpg)"></div>
    </div>

    <div class="main-panel">
        <!-- <nav class="navbar navbar-default navbar-fixed">
            <div class="container-fluid">
                <div class="navbar-header">
                    <a class="navbar-brand" href="#">Home</a>
                </div>
                <div class="collapse navbar-collapse">
                    <ul class="nav navbar-nav navbar-left">
                        <li>
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown">
								<p class="hidden-lg hidden-md">Dashboard</p>
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav> -->


        <div class="content">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-3">
                        <div class="card">
							<div class="card-body">
								<ul class="list-group">
									<div class="header">
										<h3 class="title" style="padding-bottom:20px">Current Weather</h3>
									</div>
									<li class="list-group-item" id="weatherCardHeader">
										<p style="margin:0">Clarkson University, Potsdam, NY</p>
										<p id="date" style="margin:0"><?= $dateToDisplay?></p>
									</li>
									<li class="list-group-item" style="height:60px">
										<h2 id="temp_c" style="text-align:center; margin-top:0px">
											<?php echo $tempC;?><span id="tempDisp"></span>° F
										<h2>
									</li>
									<li class="list-group-item">
                                        <h4 id="wind_speed" style="text-align:left; margin-top:0px; margin-bottom:0px">
                                            Wind Speed: <?= $windSpeed?><span id="mphDisp"></span> MPH
                                        </h4>
									</li>
									<li class="list-group-item">
										<h4 id="wind_heading" style="text-align:left; margin-top:0px; margin-bottom:0px">
											Wind Heading: <?= $windHeading?>°
										</h4>
									</li>
									<li class="list-group-item" style="height:50px">
										<h4 id="humidity" style="text-align:left; margin-top:0px; margin-bottom:0px">
											Humidity: <?= $humidity?>%
										</h4>
									</li>
									<li class="list-group-item">
										<h4 id="dewpoint_c" style="text-align:left; margin-top:0px; margin-bottom:0px">
											Dewpoint: <?= $dewpoint?>° F
										</h4>
									</li>
									<li class="list-group-item">
										<h4 id="pressure" style="text-align:left; margin-top:0px; margin-bottom:0px">
											Pressure: <?= $pressure?> mbar
										</h4>
									</li>
								</ul>
							</div>
                        </div>
                    </div>
					<div class="col-md-3">
                        <div class="card" >
							<div class="card-body">
								<ul class="list-group">
									<div class="header">
										<h3 class="title" style="padding-bottom:20px">Statistics</h3>
									</div>
									<li class="list-group-item" style="height:60px">
										<h4 id="power" style="margin-top:0px">
											Instantaneous Power: <?= $power?> W
										<h4>
									</li>
									<li class="list-group-item">
										<h4 id="energy_today" style="text-align:left; margin-top:0px; margin-bottom:0px">
											Energy Generated Today: <?= $energy?> Wh
										</h4>
									</li>
									<li class="list-group-item">
										<h4 style="text-align:center; margin-top:0px; margin-bottom:0px">
											This windmill could be providing
										</h4>
										<h2 id="percent_power_usage" style="text-align: center">
											<?= $energyPercent?>%
										</h2>
										<h4 style="text-align: center">
											of your yearly home electricity usage based on performance so far today
										</h4>
										The average home consumes approximately 11,000 kWh of power per year.
									</li>
									
								</ul>
							</div>
                        </div>
                    </div>
					<div class="col-md-6">
                        <div class="card" style="height:439px">
                            <div class="header">
                                <h3 class="title">Live Feed</h3>
                            </div>
                            <div class="content" style="text-align:center">
                                <img style="-webkit-user-select:none;" src="https://zoneminder.clarkson.edu/cgi-bin-zm/zms?&monitor=15&user=viewer1&pass=media4u" width="700" height="356">
                            </div>
                        </div>
                    </div>
                </div>

				<div class="row">
					<div class="col-md-12">
						<div class="card">
							<div class="header">
								<h3 class="title">Power Generation</h3>
							</div>
							<div class="content">
								<div style="height: 450px">
									<canvas id="mainPageLineGraph"></canvas>
								</div>
							</div>
						</div>
					</div>
				</div>
            </div>
        </div>


        <!-- <footer class="footer">
            <div class="container-fluid">
                <nav class="pull-left">
                    <ul>
                        <li>
                            <a href="#">
                                Home
                            </a>
                        </li>
                        <li>
                            <a href="#">
                                Company
                            </a>
                        </li>
                        <li>
                            <a href="#">
                                Portfolio
                            </a>
                        </li>
                        <li>
                            <a href="#">
                               Blog
                            </a>
                        </li>
                    </ul>
                </nav>
                <p class="copyright pull-right">
                    &copy; <script>document.write(new Date().getFullYear())</script> <a href="http://www.creative-tim.com">Creative Tim</a>, made with love for a better web
                </p>
            </div>
        </footer> -->

    </div>
</div>


</body>

    <!--   Core JS Files   -->
    <script src="assets/js/jquery.3.2.1.min.js" type="text/javascript"></script>
	<script src="assets/js/bootstrap.min.js" type="text/javascript"></script>
	

	<!--  Charts Plugin -->
	<script src="assets/js/chartist.min.js"></script>



    <!-- Light Bootstrap Table Core javascript and methods for Demo purpose -->
	<!-- <script src="assets/js/light-bootstrap-dashboard.js?v=1.4.0"></script> -->

	<!-- Light Bootstrap Table DEMO methods, don't include it in your project! -->
	<!-- <script src="assets/js/demo.js"></script> -->
	
	<!-- Test script for line graph -->
	<script src="custom/getdata.js"></script>
	
	<!-- chartjs import -->
	<script type="text/javascript" src="assets/lib/chartjs/Chart.min.js"></script>
	
	
	<script type="text/javascript">
    	$(document).ready(function(){

    	});
	</script>

</html>