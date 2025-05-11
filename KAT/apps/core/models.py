# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Events(models.Model):
    student_id = models.FloatField(db_column='student id', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    student_name = models.TextField(db_column='Student name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    event_id = models.TextField(db_column='Event-id', primary_key=True, default='0')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    event_name = models.TextField(db_column='Event Name', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    claim = models.CharField(max_length=500, default="No claim")
    claim_url = models.TextField(db_column='claim-url', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    posturl = models.TextField(blank=True, null=True)
    label = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'Events'
class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True)  # or IntegerField if manually set
    post_id = models.IntegerField(db_column='post-id', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    commenttext = models.TextField(blank=True, null=True)
    commenter_name = models.TextField(db_column='commenter name', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    likescount_on_comment = models.TextField(db_column='likescount on comment', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    comment_label = models.TextField(db_column='comment label', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    label = models.TextField(db_column='final_label', blank=True, null=True)  # Field name made lowercase.
    annotatorOne_comment_label = models.TextField(db_column='annotatorOne_comment_label', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    annotatorTwo_comment_label = models.TextField(db_column='annotatorTwo_comment_label', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    annotatorThree_comment_label = models.TextField(db_column='annotatorThree_comment_label', blank=True, null=True)  # Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'comments'

class PostFeatures(models.Model):
    #event_id = models.CharField(db_column='Event-id', max_length=7) 
    event = models.ForeignKey(Events, db_column='Event-id', on_delete=models.CASCADE, related_name='posts', null=True)
    post_id = models.IntegerField(db_column='post-id', primary_key=True, default=0) 
    post_url = models.TextField(db_column='post-url', blank=True, null=True) 
    platform = models.TextField(blank=True, null=True)
    post_title = models.TextField(db_column='post-title', blank=True, null=True)
    post_label = models.TextField(db_column='post-label', blank=True, null=True)
    image_image_0_video_1_if_no_image_video_2_field = models.IntegerField(db_column='image(image 0, video 1, if no image video 2)', blank=True, null=True) 
    likescount = models.TextField(blank=True, null=True)
    timestamp = models.TextField(blank=True, null=True)
    commentscount = models.TextField(blank=True, null=True)
    views = models.TextField( blank=True, null=True)
    shares = models.TextField( blank=True, null=True)
    reposts = models.TextField( blank=True, null=True)
    annotatorOne_post_label = models.TextField(db_column='annotatorOne_post_label', blank=True, null=True, ) 
    annotatorTwo_post_label = models.TextField(db_column='annotatorTwo_post_label',  blank=True, null=True)  
    annotatorThree_post_label = models.TextField(db_column='annotatorThree_post_label', max_length=25, blank=True, null=True) 
    final_label = models.TextField(db_column='final_label', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'post_features'


class UserFeatures(models.Model):
    post_id = models.IntegerField(db_column='post-id', primary_key=True, default=0)
    username = models.CharField(blank=True, null=True, max_length=51)
    followers = models.CharField(blank=True, null=True, max_length=17)
    followings = models.CharField(blank=True, null=True, max_length=20)
    is_user_verified_0_verified_1_unverified_field = models.IntegerField(db_column='is user verified(0 verified, 1 unverified)', blank=True, null=True) 
    profile_pic_url = models.TextField(db_column='profile pic url', blank=True, null=True)
    posts_count = models.CharField(db_column='posts count', blank=True, null=True, max_length=13) 
    joining_date = models.CharField(db_column='joining date', blank=True, null=True, max_length=24)

    class Meta:
        managed = True
<<<<<<< HEAD
        db_table = 'user_features'
=======
        db_table = 'user_features'
>>>>>>> 9de90cfcffcc4e4b24aca63eed9e9c2a98b21847
