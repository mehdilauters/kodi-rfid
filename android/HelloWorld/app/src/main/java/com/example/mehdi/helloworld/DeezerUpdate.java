package com.example.mehdi.helloworld;

import android.os.AsyncTask;
import android.util.Log;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;


/**
 * Created by mehdi on 10/04/17.
 */

class DeezerUpdate extends AsyncTask<MainActivity, Integer, Void> {

    MainActivity m_activity;

    public DeezerUpdate(MainActivity activity) {
        this.m_activity = activity;
    }

    protected Void doInBackground(MainActivity... activity) {

        String serial = "2102232";

        Log.i("Message", "Download");
        JSONObject jObject = null;
        //final TextView tv1 = (TextView)activity.setContentView().findViewById(R.id.hello_text);
        //final TextView tv1 = (TextView) this.m_activity.findViewById(R.id.hello_text);
        //tv1.setText("run");
        //activity[0].
        //this.m_activity.message("youhouuu");
        URL yahoo = null;
        try {
            yahoo = new URL("https://deezer.lauters.fr/deezer.json?serial=" + serial);
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
            //tv1.setText(all);
            Log.i("Message", all);
            jObject = new JSONObject(all);
            String type = jObject.getString("type");
            Log.i("Message", type);
            if(type.equals("artist")) {
                long artistid = jObject.getLong("id");

                // start playing music
                Log.i("Message", String.valueOf(artistid));
                activity[0].m_artistPlayer.playArtistRadio(artistid);
            }
        } catch (Exception e) {
            String text;
            text = "Exception...\n" + e.getMessage() + "\n" + e.toString();
            e.printStackTrace();
            //tv1.setText(text);
            Log.i("Message", text);
        }
        return null;
    }

    protected void onProgressUpdate(Integer progress) {
        //setProgressPercent(progress);
        Log.i("Message", "youhouuuuppp");
    }

    protected void onPostExecute(Long result) {
        //showDialog("Downloaded " + result + " bytes");
        this.m_activity.message("youhouuu");
        Log.i("Message", "youhouuuu");
    }
}
