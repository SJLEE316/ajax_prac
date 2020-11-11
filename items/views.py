from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required #login되어 있니..?
from django.views.decorators.http import require_POST #POST인 경우에만 실행해!
from django.http import HttpResponse #response함수
import json #json형식으로 변환
from django.template.loader import render_to_string

def main(request):
    items = Post.objects.all()
    return render(request, 'items/home.html', {'items':items})

def new(request):
    return render(request, 'items/new.html')

def create(request):
    if request.method=="POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        user = request.user
        Post.objects.create(title=title, content=content, image=image,user=user)
    return redirect('main')

def show(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.view_count = post.view_count+1
    post.save()
    user = request.user
    context = {
        'post':post, 
        'user':user,
        'comments': post.comments.all().order_by('-created_at')
    }
    return render(request, 'items/show.html', context)


#삭제하기
def delete(request,post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('main')

@require_POST
@login_required
def like_toggle(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_like, post_like_created = Like.objects.get_or_create(user=request.user, post = post) #변수 두개 만들기

    if not post_like_created: #false. 이미 누가 좋아요 눌렀어!
        post_like.delete() #눌렀으니까 삭제~
        result = "like_cancel" #result 변수 만들어서 좋아요 취소 담았음
    else:
        result = "like" #안눌렀으면 좋아요 누르기
    
    context = {
        "like_count" : post.like_count, #post모델의 like_count 불러옴
        "result" : result
    }
    return HttpResponse(json.dumps(context), content_type = "application/json")
    
@login_required
@require_POST
def dislike_toggle(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_dislike, post_dislike_created = Dislike.objects.get_or_create(user=request.user, post=post)

    if not post_dislike_created:
        post_dislike.delete()
        result = "dislike_cancel"
    else:
        result = "dislike"

    context = {
        "dislike_count":post.dislike_count,
        "result":result
    }
    return HttpResponse(json.dumps(context), content_type="application/json")     


#댓글달기
def create_comment(request, post_id):
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    content = request.POST.get('content')
    comment = Comment.objects.create(writer=user, post=post, content=content)    
    rendered = render_to_string('comments/_comment.html', { 'comment': comment, 'user': request.user})    
    context = {
        'comment': rendered
    }
    return HttpResponse(json.dumps(context), content_type="application/json")