[![Build Status](https://travis-ci.org/brunorijsman/rift-negative-disaggregation-rib-to-fib-protoype?branch=master)](https://travis-ci.org/brunorijsman/rift-negative-disaggregation-rib-to-fib-protoype)   [![Code Coverage](https://codecov.io/gh/brunorijsman/rift-negative-disaggregation-rib-to-fib-protoype/branch/master/graph/badge.svg)](https://codecov.io/gh/brunorijsman/rift-negative-disaggregation-rib-to-fib-protoype)

The [Routing In Fat Trees (RIFT)](https://datatracker.ietf.org/group/rift/about/) protocol
supports a feature called "negative disaggregation".

Instead of advertising a large number of routes for prefixes that a RIFT router *can* reach, the
RIFT router may instead choose to advertise a small number of aggregate routes (typically a
single default route) plus a small number of "exceptions" in the form of a list of prefixes that
the router *cannot* reach. That list of "exceptions" is called a negative disaggregation route.

This is very beneficial in data centers using a fat tree topology (also known as a Clos topology).
If there are no failures (failed links or failed routers) in the fat tree topology, leaf nodes
(top of rack switches) only need a single equal cost multi-path (ECMP) route that distributes the
north-bound and east-west traffic equally across all spine switches. There is no need for a very
large number of specific routes (e.g. IPv4 /32 routes) to the servers or virtual machines in the
data center. 

However, using a default route only may cause black holes when certain links or routers fail.

With negative disaggregation, the routers can advertise a negative disaggregate route, instructing
other routers in the network that they are *unable* to reach some specific prefixes. This
information is advertised in a link state packet, called a topology information element (TIE) in
RIFT.

The other RIFT routers in the network install routes with special nexthops (so-called negative
nexthops) in their routing information base (RIB) to indicate that traffic to the route prefix
should *avoid* the nexthops rather than be sent to it.

The concept is negative nexthops is control plane abstraction. Current implementations of the
forwarding plane do not support the concept of negative nexthops.

When the RIFT protocol software takes the routes from the routing information base (RIB) and
installs them into the forwarding information base (FIB) it must translate the RIB's negative
nexthops into corresponding "complementary" positive nexthops in the FIB.

Consider the following example:

Router R receives a normal (positive) default route with ECMP nexthops nh1, nh2, nh3, and nh4. It
installs the following route in the RIB:

    0.0.0.0/0 -> nh1, nh2, nh3, nh4

Router R also receives a "negative disaggregate" route for prefix 10.10.10.0/24 with a single
"negative nexthop" nh2. It installs the following route in the RIB, where the tilde (~) indicates
that the nexthop nh2 is negative nexthop. This route means "traffic for 10.10.10.0/24 must *not*
be sent to nexthop nh2".

    10.10.10.0/24 -> ~nh2

Now, router R takes the routes from the RIB and creates corresponding routes in the FIB.

Since the default route contains only positive nexthops, it is just copied:

    0.0.0.0/0 -> nh1, nh2, nh3, nh4

For the 10.10.10.0/24 route we must translate the negative nexthop ~nh2 into the corresponding
"complementary" positive nexthops. Consider what would have happened if the negative route 
10.10.10.0/24 did not exist. In that case traffic to 10.10.10.0/24 would have hit the default
route 0.0.0.0/24 and would be forwarded to ECMP nexthops nh1, nh2, nh3, nh4. However, the negative
route 10.10.10.0/24 says "don't send the traffic to nh2". So we "punch a hole in the ECMP set": we
remove nexthop nh2 from the set of nexthops nh1, nh2, nh3, nh4. This results in the following
route in the FIB:

    10.10.10.0/24 -> nh1, nh3, nh4

This was a very simple example involving only a single positive aggregate route and a single
negative more specific route.

The "RIB to FIB" translation gets more complicated when more routes and/or more nexthops are
involved. See slides 16 through 21 in Pascal Thubert's excellent PowerPoint presentation on negative
disaggregation. ([Link to slides](https://datatracker.ietf.org/doc/slides-103-rift-negative-disaggregation/))

This repository contains a prototype implementation of the code to convert RIB routes into FIB
routes, converting negative nexthops in the RIB into complementary positive nexthops in the FIB.
