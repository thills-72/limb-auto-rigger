# Limb Auto Rigger

## Demo
Demo Video: <URL>

## GitHub Repository
GitHub Repo: https://github.com/thills-72/limb-auto-rigger

## Description
This auto-rigging script is built to run inside of Maya using the
Maya Python command library integrated natively. It does not make use
of the Maya OpenAPI and as such executes some additional math that could
be bypassed thorugh OpenAPI calls.

### Features
There are three primary features: an ik/fk switch, orientation-agnostic
ribbon constructor and a user decided skinning joint density function. The
ik/fk switch and ribbon controls are attributes within the wave shaped control
placed at the final child joint location. At the moment modulating the skinning
joint density can only be done inside of the script.

### Future Development
A stretch switch for ik mode is also in development, as well as a non-deformer
or blendshape reliant implementation of twist and wave. A gui for choosing 
skinning density, alternative ribbon deformation calculations and implementation 
on a two joint or 4+ joint chain is another area of development interest, as 
well as responsive control sizing and pole-vector placement based on joint 
translation size.