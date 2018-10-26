function onSignIn(googleUser) {
  var id_token = googleUser.getAuthResponse().id_token;
  console.log("Retrieved credentials using Google as idnetity provider");

  AWS.config.region = 'us-west-2'; // Region
  AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-west-2:0f3bf9b3-701d-47b6-a1bb-f634fdb21fbc',
    Logins: {
       'accounts.google.com': id_token
    }
  });

  console.log("Initialized AWS Cognito Credentials");

  // Obtain AWS credentials
  AWS.config.credentials.get(function(){
    var accessKeyId = AWS.config.credentials.accessKeyId;
    var secretAccessKey = AWS.config.credentials.secretAccessKey;
    var sessionToken = AWS.config.credentials.sessionToken;
    var identityId = AWS.config.credentials.identityId;
  });
}
