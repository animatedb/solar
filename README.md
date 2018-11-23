# solar
Hopefully helpful information about installing solar for a residence

<h3>Introduction</h3>
First a couple of graphs to as an introduction, then later get into the details. A 3.24 kW grid-tied system with 12 panels was installed on August of 2018. This first graph shows the amount of electricity generated, and the amount used. This is with no electric car and pretty minimal use of other electricity.

<img src="generation/gen-use-2018-11.png">
This graph shows the amount of surplus electricity. My utility has an annual true-up program, which means the amount you owe or are paid is figured out once per year. The goal generally is to generate the same amount of electricity over the year as you use.
<img src="generation/gen-surplus-2018-11.png">

<h3>Initial Goals</h3>
I wanted to be green, so I didn't mind paying a bit more for a system that is currently needed. I would expect that I will have an electric vehicle in the future. It is also typically true that you will get paid less for the electricty that is generated than you might expect, especially since it might be the case that electrical costs could drop in the future. So currently I plan to use the excess for electric heating in the winter, which will reduce the gas furnase usage.

<h3>Figuring out Future Use</h3>
I figured out current use two ways. The first was to find the devices in the home that are using electricty. I used a Watt meter (Killawatt) to measure different devices and multiplied by estimated time of use. I am showing these numbers just to give an idea of what some devices can use.

<table>
  <tr><th>Wh/day</th><th>Device</th><th>Description</th></tr>
  <!-- Kitchen -->
  <tr><td>1232</td><td>Refrigerator</td><td>Energy rating between 435 and 470 = 450 kWh per year = 1232 Wh</td></tr>
  <tr><td>200</td><td>Microwave</td><td>1200W * .16h (10 minutes) = 360</td></tr>
  <tr><td>400</td><td>Oven</td><td>2400W * 5 hours per month / 30 days</td></tr>
  <tr><td>13</td><td>Range</td><td>800W * .5h * 5 days / 30 days</td></tr>

<!-- Entertainment/work -->
  <tr><td>540</td><td>TV</td><td>0W when off, 90W * 6h</td></tr>
  <tr><td>480</td><td>Cable Box</td><td>12-20W * 8h (19W when off, same as on?) = 20*24</td></tr>
  <tr><td>168</td><td>Computer</td><td>56W * 3h</td></tr>
  <tr><td>75</td><td>Computer Monitor</td><td>25W * 3h</td></tr>
  <tr><td>240</td><td>Cable Router</td><td>10W * 24h</td></tr>
  <tr><td>40</td><td>Home Router</td><td>5W * 8h</td></tr>

<!-- Lighting -->
  <tr><td>132</td><td>LED Living Lights</td><td>12 W * 4 lights * .7 dimmed * 3 hours = 132 Wh</td></tr>
  <tr><td>156</td><td>Office Lights</td><td>26 W * 2 lights * 3 hours = 156 Wh</td></tr>

  <tr><td>96</td><td>POE Injector</td><td>4W * 24</td></tr>
  <tr><td></td><td></td><td></td></tr>
  </table>
