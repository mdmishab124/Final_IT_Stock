
<body>
    <h1>Django IT Stock Management System</h1>
    <p>
        A Django project leveraging <strong>Django Unfold</strong> for improved admin design and functionality. 
        This guide provides step-by-step instructions for setup, database configuration, and resolving static file issues.
    </p>

<h2>Installation and Setup</h2>

<h3>Step 1: Install Required Dependencies</h3>
<p>To get started, install the following dependencies:</p>
<pre><code>pip install django-unfold
pip install mysql-connector-python
pip install mysqlclient
</code></pre>

<h3>Step 2: Configure the Database</h3>
<p>To use MySQL as your database, update the <code>DATABASES</code> settings in your <code>settings.py</code> file:</p>
<pre><code>DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_table_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'yourhost.com',
    }
}</code></pre>

<h3>Step 3: Reset Migrations (if necessary)</h3>
        <p>If there are existing migration files, delete them to avoid conflicts. Then, run the following commands to apply the database schema:</p>
        <pre><code>python manage.py makemigrations
python manage.py migrate
        </code></pre>
    </div>


<h2>Static Files Configuration</h2>
        <p>
            If the Unfold design is not displaying correctly, ensure your static files are configured properly in 
            <code>settings.py</code>:
        </p>
        <pre><code>STATIC_URL = '/static/'
STATIC_ROOT = '/yourserverstaticpath/'</code></pre>

<p>Afterward, collect static files with the following command:</p>
        <pre><code>python manage.py collectstatic</code></pre>



<h2>Usage</h2>
        <p>Once all configurations are complete, you can start the development server and explore the Django Unfold design:</p>
        <pre><code>python manage.py runserver</code></pre>


<h2>Troubleshooting</h2>
        <ul>
            <li>
                <strong>Unfold Design Not Showing:</strong> 
                Ensure static files are correctly configured and collected as outlined in the 
                <a href="#static-files-configuration">Static Files Configuration</a> section.
            </li>
            <li>
                <strong>Database Connection Issues:</strong>
                <ul>
                    <li>Verify your MySQL credentials and host information in the <code>DATABASES</code> setting.</li>
                    <li>Ensure the required MySQL libraries (<code>mysql-connector-python</code> and <code>mysqlclient</code>) are installed.</li>
                </ul>
            </li>
        </ul>


<h2>License</h2>
        <p>
            This project is licensed under the <a href="LICENSE">MIT License</a>. 
            Feel free to use, modify, and distribute.
        </p>

