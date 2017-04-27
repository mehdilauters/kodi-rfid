package com.example.mehdi.helloworld;

import android.os.Handler;
import android.support.v4.os.AsyncTaskCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

import com.deezer.sdk.network.connect.DeezerConnect;
import com.deezer.sdk.model.Permissions;
import com.deezer.sdk.network.connect.event.DialogListener;
import com.deezer.sdk.network.connect.SessionStore;
import com.deezer.sdk.player.AlbumPlayer;
import com.deezer.sdk.player.ArtistRadioPlayer;
import com.deezer.sdk.player.networkcheck.WifiAndMobileNetworkStateChecker;


public class MainActivity extends AppCompatActivity {

    public ArtistRadioPlayer m_artistPlayer = null;

    public void message(String _message) {
        final TextView tv1 = (TextView)findViewById(R.id.hello_text);
        tv1.setText(_message);
    }

    protected void play(DeezerConnect deezerConnect) {
        try {
            m_artistPlayer = new ArtistRadioPlayer(this.getApplication(), deezerConnect, new WifiAndMobileNetworkStateChecker());
            Log.i("Message", "start play");
            final TextView tv1 = (TextView)findViewById(R.id.hello_text);
            tv1.setText("Ready to play");
            final Handler handler=new Handler();
            final MainActivity self = this;
            Runnable task = new Runnable(){
                @Override
                public void run() {
                    Log.i("Message", "reload");
                    DeezerUpdate dzupdate = new DeezerUpdate(self);
                    AsyncTaskCompat.executeParallel( dzupdate, self);
                    try {
                        Thread.sleep(1000);
                        handler.post(this); // set time here to refresh textView
                    }
                    catch (Exception e)
                    {

                    }
                }
            };
            handler.post(task);

        } catch(Exception e) {
            e.printStackTrace();
            Log.i("Message", "reload exception");
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // replace with your own Application ID
        String applicationID = "215062";
        final DeezerConnect deezerConnect = new DeezerConnect(this, applicationID);


        // restore any saved session
        SessionStore sessionStore = new SessionStore();
        if (sessionStore.restore(deezerConnect, MainActivity.this)) {
            // The restored session is valid, navigate to the Home Activity
            //Intent intent = new Intent(context, HomeActivity.class);
            //startActivity(intent);
            MainActivity.this.play(deezerConnect);
        }
        else
        {
            // The set of Deezer Permissions needed by the app
            String[] permissions = new String[] {
                    Permissions.BASIC_ACCESS,
                    Permissions.MANAGE_LIBRARY,
                    Permissions.LISTENING_HISTORY };

// The listener for authentication events
            DialogListener listener = new DialogListener() {

                public void onComplete(Bundle values) {

                    // store the current authentication info
                    SessionStore sessionStore = new SessionStore();
                    sessionStore.save(deezerConnect, MainActivity.this);

                    MainActivity.this.play(deezerConnect);

                }

                public void onCancel() {}

                public void onException(Exception e) {}
            };

            // Launches the authentication process
            deezerConnect.authorize(this, permissions, listener);
        }


    }
}
