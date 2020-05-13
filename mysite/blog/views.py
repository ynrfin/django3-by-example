from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
    object_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3) # 3 post in each page
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver last page
        posts = paginator.page(paginator.num_pages)
    return render(request,
        'blog/post/list.html',
        {
            'page': page,
            'tag': tag,
            'posts': posts
        })

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create comment object but don't save to DB yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the commit
            new_comment.post = post
            # save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'new_comment': new_comment,
            'comment_form': comment_form
    })

def post_share(request, post_id):
    # REtrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd =form.cleaned_data

            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recomends you read " \
                    f"{post.title}"
            message = f"Read {post.title} at {post_url} \n\n "\
                f"{cd['name']}\'s comments: {cd['comments']}"

            send_mail(subject, message, 'mygmart1@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {
        'post': post,
        'form':form,
        'sent':sent
    })

