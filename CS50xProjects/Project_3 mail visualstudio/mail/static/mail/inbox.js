document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Handling Submit
  document.querySelector("#compose-form").addEventListener('submit', send_email)

  // By default, load the inbox
  load_mailbox('inbox');
});

function view_email(id) {
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
      // Print emails
      console.log(email);
  
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'none';
      document.querySelector('#emails-view').style.display = 'block';
      document.querySelector('#emails-view').innerHTML = `
      <h5><strong>From: </strong>${email.sender}</h5>
      <h5><strong>To: </strong>${email.recipients}</h5>
      <h5><strong>Subject: </strong>${email.subject}</h5>
      <h5><strong>Timestamp: </strong>${email.timestamp}</h5>
      <button id=('#compose') class="btn btn-primary">Reply</button>
      <hr>
      <h5>${email.body}</h5>
      `
      //Change email to read
      if(!email.read){
        fetch(`/emails/${email.id}`,{
          method: 'PUT',
          body: JSON.stringify({
            read: true
          })
        })
      }

      //Archive and unarchive logic
      const archive_button = document.createElement('button');
      archive_button.innerHTML = email.archived ? "Unarchive" : "Archive";
      archive_button.className = email.archived ? "btn btn-success" : "btn btn-danger";
      archive_button.addEventListener('click', function() {
        fetch(`/emails/${email.id}`, {
          method: 'PUT',
          body: JSON.stringify({
              archived: !email.archived
          })
        })
         .then(() => { load_mailbox('archive')})
      });
      document.querySelector('#emails-view').append(archive_button);

      //Reply 
      const reply_button = document.createElement('button');
      reply_button.innerHTML = "Reply" ;
      reply_button.className = "btn btn-primary";
      reply_button.addEventListener('click', function() {
        compose_email();

        document.querySelector('#compose-recipients').value = email.sender;
        let subject = email.subject;
        if (email.subject.split(' ',1)[0] != "Re:"){
          subject = "Re: " + email.subject;
        }
        document.querySelector('#compose-subject').value = subject;
        document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.recipients} wrote: ${email.body}`;
      });
      document.querySelector('#emails-view').append(reply_button);
  });
  
}

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Get email from mailbox for user
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(email => {
      // Loop through the emails and make a div for each
      
      email.forEach(singleEmail => {

        // make a div for each email
        const newEmail = document.createElement('div');
        //newEmail.className= 
        newEmail.innerHTML = `<h3>Sender: ${singleEmail.sender}</h1>
                              <h3>Subject: ${singleEmail.subject}</h1>
                              <p>Timestamp: ${singleEmail.timestamp}</p>
        `;

        // Read & Unread color
        newEmail.className = singleEmail.read ? 'read': 'unread';

        // If clicked to view email
        newEmail.addEventListener('click', function() {
            view_email(singleEmail.id)
            console.log('This element has been clicked!')
        });
        document.querySelector('#emails-view').append(newEmail);
      });
    

    // ... do something else with email ...
});
}

function send_email(event) {
  event.preventDefault();
  
  const recipient = document.querySelector('#compose-recipients').value
  const subject = document.querySelector('#compose-subject').value
  const body = document.querySelector('#compose-body').value

  fetch(`/emails`, {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipient,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox('sent');
  });

}