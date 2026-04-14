# Ribbon Rig Auto-Builder

## Repository
https://github.com/thills-72/limb-auto-rigger

## Description
This program is designed to assist in the auto-completion of limb rigs by
creating an ik and fk switch with an fk ribbon rig overlay.

## Features
- IK/FK Creation
	- Creates an IK and FK rig set-up by duplicating the selected limb chain,
    establishing the controls and parenting the original to the created while 
    adding the switch attributes needed.
- Squash/Stretch IK/FK
    - The IK/FK skeletons have an additional attribute which allows for toggling
    of squash and stretch features.
- Ribbon Creation
	- A ribbon overlay system is created with a crease at the middle joint,
    a set amount of additional fk controls, and which allows for seamless
    use of the base IK/FK system.
- Ribbon Blendshape Deformers
    - Establishes two blendshapes in the shape editor with a twist and
    sine deformer for the ribbon.

## Challenges
- Understand ribbons, their pitfalls and advantages, and how to set them up
  in more detail.
- Learn how to work with CV's and NURB planes in the Maya python API.
- Learn how to tie multiple classes together to create an adaptive system
  that can be responsive to multiple different kinds of inputs.
- Learn how to layer together the IK/FK system while enabling ribbon based features.

## Outcomes
Ideal Outcome:
- A modular limb rigging tool that can easily create a basic, flexible set-up
  quickly. Should allow for cartoony motion or more realistic motion with
  set attributes to allow animators to decide what direction they want to go.

Minimal Viable Outcome:
- A tool that auto-builds an IK/FK switch limb system.

## Milestones

- Week 1
  1. Understand ribbons.
  2. Have a script that builds an IK and FK set-up individually.

- Week 2
  1. Push the IK and FK scripts into individual classes and tie them
  together with another class.
  2. Build a script that can create a ribbon with controls.

- Week N (Final)
  1. Script the shape editor additions within the ribbon class.
  2. Integrate the ribbon script into the overall limb creation class.
  3. Film and submit the demo.