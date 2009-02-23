+++++++++++++++++++
Data Model Overview
+++++++++++++++++++

Entities
========

Every entity has these attributes:

* name: text, must be globally unique
* title: text, should be under 80-characters long
* description: text, as long as you want
* created date
* modified date
* creator
* last modified by
* type: must be any of
    * task
    * task status
    * milestone
    * milestone status
    * person
    * component
    * comment

Tasks
=====

Task entities also have these attributes:

* status 
* owners (refers to people)
* milestone 
* components 
* comments

Milestones
==========

Milestone entities also have these attributes:

* release date
* milestone status
* comments

Backlinks
=========

When a task is linked to a milestone, it is also true to say that the
milestone's list of tasks now includes that task.  However, strictly
speaking, the milestone entity does not have a "tasks" attribute.
