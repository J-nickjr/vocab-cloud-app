# ✅ 已優化為 Web App 專用版本 views.py

import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

import google.generativeai as genai
import google.api_core.exceptions

from .models import SearchHistory

from django.http import HttpResponse
from accounts.forms import SignUpForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from accounts.forms import SignUpForm  # 用剛剛的含 email 表單
from django.contrib.auth.models import User



# ✅ 載入 .env 的環境變數
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Gemini 查詞邏輯
def ai_define(word):
    prompt = f"""
請幫我用以下格式解釋這個英文單字：「{word}」。

🌛 "{word}"
意思：<簡要解釋該詞語的含義和背景>。
這裡的 <關鍵詞語義或詞源的解釋>，引申出<具體語境的意思>。

例句：
❶ <例句1英文>
<例句1翻譯>

❷ <例句2英文>
<例句2翻譯>

❸ <例句3英文>
<例句3翻譯>

👉 應用場景：<描述該詞語或片語常用的場景或用途>

請使用 **簡單英文**與**繁體中文**（台灣用語），保持格式與標點。
"""
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)
    return (response.text or "").strip()

# ✅ 首頁：若登入自動導向查詢頁，未登入導向登入頁
def home(request):
    if request.user.is_authenticated:
        return redirect('search_word')
    return redirect(reverse('login'))

# ✅ 註冊功能
def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False                 # 先鎖住，等 email 驗證
            user.email = form.cleaned_data["email"]
            user.save()
            send_activation_email(request, user)
            return render(request, "registration/activation_sent.html")
    else:
        form = SignUpForm()

    return render(request, "registration/register.html", {"form": form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  # 啟用後直接登入
        return render(request, "registration/activation_complete.html")
    else:
        return render(request, "registration/activation_invalid.html", status=400)



# ✅ 查詢畫面與邏輯（只查詢，不寫 DB）
@login_required
def search_word(request):
    definition = ""
    word = ""
    error = ""

    if request.method == "POST":
        word = (request.POST.get("word") or "").strip()
        now = timezone.now()
        print(f"🟢 使用者送出查詢：{word}，時間：{now}")

        if word:
            try:
                definition = ai_define(word)
                print("✅ 成功從 Gemini 取得定義")
            except google.api_core.exceptions.ResourceExhausted as e:
                print("❌ Gemini API 回傳 ResourceExhausted（封鎖）")
                print("🔍 錯誤訊息內容：", e)
                error = "⚠️ 查詢次數過多，請等 300 秒再試。"
            except Exception as e:
                print("❌ 其他未知錯誤：", e)
                error = "❌ 發生未知錯誤，請稍後再試。"

        # 🔕 這裡**不再**自動寫入資料庫
        # 只有按下「加入單字庫」才會進 add_word() 儲存

    return render(request, 'vocab/search.html', {
        "definition": definition,
        "word": word,
        "error": error,
    })

# ✅ 查詢歷史紀錄頁
@login_required
def history(request):
    histories = SearchHistory.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "vocab/history.html", {"histories": histories})

# ✅ 新增到單字庫（只有按按鈕才寫 DB）
@require_POST
@login_required
def add_word(request):
    word = (request.POST.get("word") or "").strip()
    definition = (request.POST.get("definition") or "").strip()

    if word and definition:
        # 避免重複：同一使用者 + 同一單字只存一筆（不區分大小寫）
        if not SearchHistory.objects.filter(user=request.user, word__iexact=word).exists():
            SearchHistory.objects.create(user=request.user, word=word, definition=definition)

    # 回到查詢頁並保留關鍵字
    return redirect(f"{reverse('search_word')}?q={word}")

# ✅ 刪除單一查詢紀錄
@login_required
def delete_history(request, pk):
    history = get_object_or_404(SearchHistory, pk=pk, user=request.user)
    history.delete()
    return redirect('history')

# ✅ 清空全部查詢紀錄
@login_required
def clear_history(request):
    SearchHistory.objects.filter(user=request.user).delete()
    return redirect('history')

def health(request):
    return HttpResponse("ok")


@require_http_methods(["GET", "POST"])
def logout_then_home(request):
    logout(request)
    return redirect("home")  # 登出後回首頁

@require_http_methods(["GET", "POST"])
def logout_and_redirect_login(request):
    logout(request)
    return redirect("login")  # 直接去 /accounts/login/

def send_activation_email(request, user: User):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activate_url = request.build_absolute_uri(
        reverse("activate", args=[uidb64, token])
    )
    subject = "請啟用你的帳號"
    message = render_to_string("registration/activation_email.txt", {
        "user": user,
        "activate_url": activate_url,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
