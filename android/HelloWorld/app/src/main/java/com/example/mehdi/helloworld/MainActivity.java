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

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;


public class MainActivity extends AppCompatActivity {

    public ArtistRadioPlayer m_artistPlayer = null;

    public void message(String _message) {
        final TextView tv1 = (TextView)findViewById(R.id.hello_text);
        tv1.setText(_message);
    }

    void play_thread() {
        Config config = new Config();

        Log.i("Message", "Download");
        JSONObject jObject = null;
        final TextView tv1 = (TextView) this.findViewById(R.id.hello_text);
        URL yahoo = null;
        try {
            yahoo = new URL("https://"+config.host+"/deezer.json?serial=" + config.serial);
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }
        Log.i("Message", yahoo.toString());
        try {
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(
                            yahoo.openStream()));


            String inputLine;
            String all = "";

            while ((inputLine = in.readLine()) != null)
                all += inputLine;

            in.close();

            final String disp = all;
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    tv1.setText(disp);
                }
            });

            Log.i("Message", all);
            jObject = new JSONObject(all);
            String type = jObject.getString("type");
            Log.i("Message", type);
            if(type.equals("artist")) {
                long artistid = jObject.getLong("id");

                // start playing music
                Log.i("Message", String.valueOf(artistid));
                m_artistPlayer.playArtistRadio(artistid);
            }
        } catch (Exception e) {
            String text;
            text = "Exception...\n" + e.getMessage() + "\n" + e.toString();
            e.printStackTrace();
            //tv1.setText(text);
            Log.i("Message", text);
        }
    }

    protected void play(DeezerConnect deezerConnect) {
        try {
            m_artistPlayer = new ArtistRadioPlayer(this.getApplication(), deezerConnect, new WifiAndMobileNetworkStateChecker());
            Log.i("Message", "start play");
            final TextView tv1 = (TextView)findViewById(R.id.hello_text);
            tv1.setText("Ready to play");

            new Thread(new Runnable() {
                @Override
                public void run() {
                    try {
                        while (true) {
                            play_thread();
                            Thread.sleep(500);
                        }
                    } catch (Exception e) {
                    }
                    Log.i("Message", "thread exit");
                }
            }).start();

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
